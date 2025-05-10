import asyncio
import logging
from typing import Any, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    Response,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from sqlalchemy.orm import Session
from bson.objectid import ObjectId
from pydantic import parse_obj_as
from pymongo.collection import ReturnDocument

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
    validate_ue,
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

    retrieved_docs = [
        doc["subscription"]
        for doc in db_mongo[db_collection].find(
            {"owner_id": current_user.id},
            projection={"_id": False, "subscription": True},
        )
        if filter_active_subscription(db_mongo, doc)
    ]

    http_response = JSONResponse(content=retrieved_docs, status_code=200)
    add_notifications(http_request, http_response, False)
    return http_response


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
async def create_subscription(
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
        id_value = str(item_in.ipv4Addr)
        ue = crud_ue.get_ipv4(db=db, ipv4=id_value, owner_id=current_user.id)

    elif item_in.ipv6Addr is not None:
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
                locationInfo=LocationInfo(
                    geographicArea=Point(
                        shape="POINT",
                        point=GeographicalCoordinates(
                            lat=ue.latitude, lon=ue.longitude
                        ),
                    ),
                ),
            )

            if ue.Cell_id and response.locationInfo:
                response.locationInfo.cellId = ue.Cell_id

            serialized_report = jsonable_encoder(response.dict(exclude_unset=True))

            http_response = JSONResponse(content=serialized_report, status_code=200)
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

    if item_in.monitoringType == MonitoringType.LOCATION_REPORTING:
        # Create the reference resource and location header
        response_header = {"Location": item_in.self}

        if item_in.immediateRep:
            asyncio.create_task(handle_location_report_callback(json_data, ue, id))

        http_response = JSONResponse(
            content=json_data, status_code=201, headers=response_header
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

        if (
            item_in.immediateRep
            and item_in.monitoringType == MonitoringType.LOSS_OF_CONNECTIVITY
        ):
            asyncio.create_task(
                handle_loss_connectivity_callback(
                    inserted_doc, ue, id, ue.Cell_id, ue.Cell_id
                )
            )

        elif (
            item_in.immediateRep
            and item_in.monitoringType == MonitoringType.UE_REACHABILITY
        ):
            asyncio.create_task(
                handle_ue_reachability_callback(
                    inserted_doc, ue, id, ue.Cell_id, ue.Cell_id
                )
            )

        # Create the reference resource and location header
        response_header = {"Location": item_in.self}

        http_response = JSONResponse(
            content=json_data, status_code=201, headers=response_header
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

    retrieved_doc = get_subscription_document(db_mongo, subscriptionId, current_user)

    # Check if the document exists
    if not retrieved_doc:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if filter_active_subscription(db_mongo, retrieved_doc):
        # Update the document
        json_data = jsonable_encoder(item_in, exclude_unset=True)
        updated_doc = db_mongo[db_collection].find_one_and_update(
            {"_id": ObjectId(subscriptionId)},
            {"$set": {"subscription": json_data}},
            projection={"_id": False, "subscription": True},
            return_document=ReturnDocument.AFTER,
        )["subscription"]

        http_response = JSONResponse(content=updated_doc, status_code=200)
        add_notifications(http_request, http_response, False)
        return http_response

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

    retrieved_doc = get_subscription_document(db_mongo, subscriptionId, current_user)

    # Check if the document exists
    if not retrieved_doc:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if filter_active_subscription(db_mongo, retrieved_doc):
        http_response = JSONResponse(content=retrieved_doc, status_code=200)

        add_notifications(http_request, http_response, False)
        return http_response

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

    retrieved_doc = get_subscription_document(db_mongo, subscriptionId, current_user)

    # Check if the document exists
    if not retrieved_doc:
        raise HTTPException(status_code=404, detail="Subscription not found")

    db_mongo[db_collection].delete_one({"_id": ObjectId(subscriptionId)})

    http_response = JSONResponse(content=retrieved_doc, status_code=200)
    add_notifications(http_request, http_response, False)
    return http_response


def get_subscription_document(db_mongo, subscriptionId, current_user):
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
    return retrieved_doc
