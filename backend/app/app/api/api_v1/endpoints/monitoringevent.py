from typing import Any, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    Response,
    BackgroundTasks,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from sqlalchemy.orm import Session
from bson.objectid import ObjectId
from pydantic import parse_obj_as

from app import models, schemas, tools
from app.api import deps
from app.api.api_v1.endpoints.utils import add_notifications
from app.crud import crud_mongo
from app.crud import ue as crud_ue
from app.crud import user
from app.db.session import client
from app.schemas.commonData import Link
from app.schemas.monitoringevent import (
    GeographicalCoordinates,
    LocationInfo,
    MonitoringEventReport,
    MonitoringType,
    Point,
)
from app.schemas.commonData import Link
from app.crud import crud_mongo, ue as crud_ue, user

from .ue_movement import (
    handle_location_report_callback,
    handle_loss_connectivity_callback,
    handle_ue_reachability_callback,
)
from .utils import ReportLogging

router = APIRouter()
router.route_class = ReportLogging
db_collection = "MonitoringEvent"


def filter_active_subscription(db_mongo, sub):
    sub_validate_time = tools.check_expiration_time(
        expire_time=sub.get("monitorExpireTime")
    )
    if not sub_validate_time:
        crud_mongo.delete_by_item(
            db_mongo, db_collection, "externalId", sub.get("externalId")
        )

    return sub_validate_time


@router.get(
    "/{scsAsId}/subscriptions",
    response_model=List[schemas.MonitoringEventSubscription],
    responses={200: {"model": List[schemas.MonitoringEventSubscription]}},
)
def read_active_subscriptions(
    *,
    scsAsId: str = Path(
        ...,
        title="The ID of the Netapp that read all the subscriptions",
        example="myNetapp",
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request,
) -> Any:
    """
    Read all active subscriptions
    """
    db_mongo = client.fastapi

    retrieved_docs = list(
        filter(
            lambda x: filter_active_subscription(db_mongo, x),
            map(
                lambda doc: doc["subscription"],
                db_mongo[db_collection].find(
                    {"owner_id": current_user.id},
                    projection={"_id": False, "subscription": True},
                ),
            ),
        )
    )

    if retrieved_docs:

        http_response = JSONResponse(content=retrieved_docs, status_code=200)
        add_notifications(http_request, http_response, False)
        return http_response

    return JSONResponse(content=[], status_code=200)


# Callback

monitoring_callback_router = APIRouter()


@monitoring_callback_router.post(
    "{$request.body.notificationDestination}",
    status_code=204,
    response_class=Response,
)
def monitoring_notification(body: schemas.MonitoringNotification):
    pass


@router.post(
    "/{scsAsId}/subscriptions",
    response_model=schemas.MonitoringEventSubscription,
    responses={201: {"model": schemas.MonitoringEventSubscription}},
    callbacks=monitoring_callback_router.routes,
)
def create_subscription(
    *,
    scsAsId: str = Path(
        ...,
        title="The ID of the Netapp that creates a subscription",
        example="myNetapp",
    ),
    db: Session = Depends(deps.get_db),
    item_in: schemas.MonitoringEventSubscription,
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create new subscription.
    """
    if item_in.self is not None:
        raise HTTPException(
            status_code=400, detail="The self attribute must not be set"
        )

    db_mongo = client.fastapi

    ue = None

    id = ObjectId()
    item_in.self = parse_obj_as(Link, f"{http_request.url}/{id}")

    if item_in.ipv4Addr is not None:
        print("The IPv4 Addr is", str(item_in.ipv4Addr))
        id_value = str(item_in.ipv4Addr)
        ue = crud_ue.get_ipv4(db=db, ipv4=id_value, owner_id=current_user.id)

    elif item_in.ipv6Addr is not None:
        print("The IPv6 Addr is", item_in.ipv6Addr.exploded)
        id_value = item_in.ipv6Addr.exploded
        ue = crud_ue.get_ipv6(db=db, ipv6=id_value, owner_id=current_user.id)

    elif item_in.externalId:
        ue = crud_ue.get_externalId(
            db=db, externalId=item_in.externalId.__root__, owner_id=current_user.id
        )

    elif item_in.msisdn:
        ue = crud_ue.get_msisdn(
            db=db, msisdn=item_in.msisdn.__root__, owner_id=current_user.id
        )

    if not ue:
        raise HTTPException(
            status_code=404, detail="UE with this identifier doesn't exist"
        )

    isByMaxReports = item_in.maximumNumberOfReports is not None

    isByExpireTime = item_in.monitorExpireTime is not None

    if not (isByExpireTime or isByMaxReports):
        raise HTTPException(
            status_code=400,
            detail="The request must contain either a maximumNumberOfReports or a monitorExpireTime",
        )

    # One time request
    if item_in.maximumNumberOfReports == 1:
        if item_in.monitoringType == MonitoringType.LOCATION_REPORTING:

            response = MonitoringEventReport(
                msisdn=ue.msisdn,
                monitoringType=item_in.monitoringType,
            )
            if ue.Cell_id:
                response.locationInfo = LocationInfo(
                    cellId=ue.Cell_id,
                    geographicArea=Point(
                        shape="POINT",
                        point=GeographicalCoordinates(
                            lat=ue.latitude, lon=ue.longitude
                        ),
                    ),
                )
            else:
                response.locationInfo = LocationInfo(
                    geographicArea=Point(
                        shape="POINT",
                        point=GeographicalCoordinates(
                            lat=ue.latitude, lon=ue.longitude
                        ),
                    ),
                )

            serialized_subscription = jsonable_encoder(
                response.dict(exclude_unset=True)
            )

            http_response = JSONResponse(
                content=serialized_subscription, status_code=200
            )
            add_notifications(http_request, http_response, False)

            return http_response

        if item_in.monitoringType in (
            MonitoringType.LOSS_OF_CONNECTIVITY,
            MonitoringType.UE_REACHABILITY,
        ):
            return JSONResponse(
                content=jsonable_encoder(
                    {
                        "title": "Not Supported",
                        "invalidParams": {
                            "param": "maximumNumberOfReports",
                            "reason": '"maximumNumberOfReports" should be greater than 1 in case of LOSS_OF_CONNECTIVITY or UE_REACHABILITY event',
                        },
                    }
                ),
                status_code=400,
            )

    # Subscription
    if item_in.monitoringType == MonitoringType.LOCATION_REPORTING:

        item_in.ipv4Addr = ue.ip_address_v4
        json_data = jsonable_encoder(item_in.dict(exclude_unset=True))

        inserted_doc = crud_mongo.create(
            db_mongo,
            db_collection,
            {
                "_id": id,
                "supi": ue.supi,
                "subscription": json_data,
                "owner_id": current_user.id,
            },
        )

        # Create the reference resource and location header
        response_header = {"Location": item_in.self}

        # Retrieve the updated document | UpdateResult is not a dict
        updated_doc = crud_mongo.read_uuid(
            db_mongo, db_collection, inserted_doc.inserted_id
        )["subscription"]

        if item_in.immediateRep:
            background_tasks.add_task(handle_location_report_callback, updated_doc, ue)

        http_response = JSONResponse(
            content=updated_doc, status_code=201, headers=response_header
        )
        add_notifications(http_request, http_response, False)

        return http_response
    if item_in.monitoringType in (
        MonitoringType.LOSS_OF_CONNECTIVITY,
        MonitoringType.UE_REACHABILITY,
    ):
        # Check if subscription with externalid && monitoringType exists
        if crud_mongo.read_by_multiple_pairs(
            db_mongo,
            db_collection,
            externalId=item_in.externalId and item_in.externalId.__root__,
            monitoringType=item_in.monitoringType,
        ):
            raise HTTPException(
                status_code=409,
                detail=f"There is already an active subscription for UE with external id {item_in.externalId} - Monitoring Type = {item_in.monitoringType}",
            )

        item_in.ipv4Addr = ue.ip_address_v4
        json_data = jsonable_encoder(item_in.dict(exclude_unset=True))

        inserted_doc = crud_mongo.create(
            db_mongo,
            db_collection,
            {
                "_id": id,
                "supi": ue.supi,
                "subscription": json_data,
                "owner_id": current_user.id,
            },
        )

        if (
            item_in.immediateRep
            and item_in.monitoringType == MonitoringType.LOSS_OF_CONNECTIVITY
        ):
            background_tasks.add_task(
                handle_loss_connectivity_callback,
                inserted_doc,
                ue,
                ue.Cell_id,
                ue.Cell_id,
            )

        elif (
            item_in.immediateRep
            and item_in.monitoringType == MonitoringType.UE_REACHABILITY
        ):
            background_tasks.add_task(
                handle_ue_reachability_callback,
                inserted_doc,
                ue,
                ue.Cell_id,
                ue.Cell_id,
            )

        # Create the reference resource and location header
        response_header = {"Location": item_in.self}

        # Retrieve the updated document | UpdateResult is not a dict
        updated_doc = crud_mongo.read_uuid(
            db_mongo, db_collection, inserted_doc.inserted_id
        )["subscription"]

        http_response = JSONResponse(
            content=updated_doc, status_code=201, headers=response_header
        )
        add_notifications(http_request, http_response, False)

        return http_response


@router.put(
    "/{scsAsId}/subscriptions/{subscriptionId}",
    response_model=schemas.MonitoringEventSubscription,
)
def update_subscription(
    *,
    scsAsId: str = Path(
        ...,
        title="The ID of the Netapp that creates a subscription",
        example="myNetapp",
    ),
    subscriptionId: str = Path(..., title="Identifier of the subscription resource"),
    item_in: schemas.MonitoringEventSubscription,
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request,
) -> Any:
    """
    Update/Replace an existing subscription resource
    """
    db_mongo = client.fastapi

    try:
        id = ObjectId(subscriptionId)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid uuid (24-character hex string)",
        )

    filters = {"_id": id}
    if not user.is_superuser(current_user):
        filters = {"owner_id": current_user.id}
    retrieved_doc = db_mongo[db_collection].find_one(
        filters, {"_id": False, "subscription": True}
    )

    # Check if the document exists
    if not retrieved_doc:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub_validate_time = tools.check_expiration_time(
        expire_time=retrieved_doc.get("monitorExpireTime")
    )

    if sub_validate_time:
        # Update the document
        retrieved_doc["subscription"] = jsonable_encoder(item_in, exclude_unset=True)
        crud_mongo.update_new_field(
            db_mongo, db_collection, subscriptionId, retrieved_doc
        )

        # Retrieve the updated document | UpdateResult is not a dict
        updated_doc = crud_mongo.read_uuid(db_mongo, db_collection, subscriptionId)[
            "subscription"
        ]

        http_response = JSONResponse(content=updated_doc, status_code=200)
        add_notifications(http_request, http_response, False)
        return http_response

    crud_mongo.delete_by_uuid(db_mongo, db_collection, subscriptionId)
    raise HTTPException(status_code=403, detail="Subscription has expired")


@router.get(
    "/{scsAsId}/subscriptions/{subscriptionId}",
    response_model=schemas.MonitoringEventSubscription,
)
def read_subscription(
    *,
    scsAsId: str = Path(
        ...,
        title="The ID of the Netapp that creates a subscription",
        example="myNetapp",
    ),
    subscriptionId: str = Path(..., title="Identifier of the subscription resource"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request,
) -> Any:
    """
    Get subscription by id
    """
    db_mongo = client.fastapi

    try:
        id = ObjectId(subscriptionId)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid uuid (24-character hex string)",
        )

    filters = {"_id": id}
    if not user.is_superuser(current_user):
        filters = {"owner_id": current_user.id}
    retrieved_doc = db_mongo[db_collection].find_one(
        filters, {"_id": False, "subscription": True}
    )["subscription"]

    # Check if the document exists
    if not retrieved_doc:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub_validate_time = tools.check_expiration_time(
        expire_time=retrieved_doc.get("monitorExpireTime")
    )

    if sub_validate_time:
        http_response = JSONResponse(content=retrieved_doc, status_code=200)

        add_notifications(http_request, http_response, False)
        return http_response

    db_mongo[db_collection].delete_one({"_id": id})
    raise HTTPException(status_code=403, detail="Subscription has expired")


@router.delete(
    "/{scsAsId}/subscriptions/{subscriptionId}",
    response_model=schemas.MonitoringEventSubscription,
)
def delete_subscription(
    *,
    scsAsId: str = Path(
        ...,
        title="The ID of the Netapp that creates a subscription",
        example="myNetapp",
    ),
    subscriptionId: str = Path(..., title="Identifier of the subscription resource"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request,
) -> Any:
    """
    Delete a subscription
    """
    db_mongo = client.fastapi

    try:
        id = ObjectId(subscriptionId)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid uuid (24-character hex string)",
        )

    filters = {"_id": id}
    if not user.is_superuser(current_user):
        filters = {"owner_id": current_user.id}
    retrieved_doc = db_mongo[db_collection].find_one(
        filters, {"_id": False, "subscription": True}
    )["subscription"]

    # Check if the document exists
    if not retrieved_doc:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db_mongo[db_collection].delete_one({"_id": id})

    http_response = JSONResponse(content=retrieved_doc, status_code=200)
    add_notifications(http_request, http_response, False)
    return http_response
