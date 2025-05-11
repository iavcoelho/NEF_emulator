import asyncio
import logging
from typing import Any, Literal, Optional


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app import crud, models, tools
from app.api import deps
from app.crud import crud_mongo
from app.db.session import client
from app.models.UE import UE
from app.schemas import Msg
from app.schemas.monitoringevent import (
    MonitoringType,
    Point,
)
from app.tools.distance import check_distance
from app.tools.rsrp_calculation import check_rsrp, check_path_loss
from app.api.deps import db_context
from app.tools.monitoring_callbacks import (
    handle_location_report_callback,
    handle_ue_reachability_callback,
    handle_loss_connectivity_callback,
)

# API
handovers = {}
router = APIRouter()

moving_devices = dict()

Speed = Literal["HIGH", "LOW"]


def increment_position(speed: Speed) -> int:
    if speed == "LOW":
        return 1

    if speed == "HIGH":
        return 10


def validate_ue(*, ue: Optional[UE], user: models.User, db) -> Optional[UE]:
    if ue is None:
        logging.warning("UE not found")
        return None

    if not user.is_superuser or ue.owner_id != user.id:
        logging.warning("Not enough permissions")
        return None

    path = crud.path.get(db=db, id=ue.path_id)

    if path is None:
        logging.warning("Path not found")
        return None

    return ue


async def movement_loop(supi: str, user: models.User):
    with db_context() as db:
        ue = validate_ue(ue=crud.ue.get_supi(db=db, supi=supi), user=user, db=db)

        if ue is None:
            moving_devices.pop(supi)
            return

        points = crud.points.get_points(db=db, path_id=ue.path_id)

        # Assume end of path
        current_position_index = -1
        cells = crud.cell.get_multi_by_owner(db=db, owner_id=user.id)

        # Find current position if one exists
        for index, point in enumerate(points):
            if (ue.latitude == point.latitude) and (ue.longitude == point.longitude):
                current_position_index = index
                break

        handovers[ue.supi] = []

        while True:
            if supi not in moving_devices:
                break

            current_position_index = (
                increment_position(ue.speed) + current_position_index
            ) % len(points)
            point = points[current_position_index]

            cell_now, _ = check_distance(point.latitude, point.longitude, cells)

            ue = crud.ue.update_coordinates(
                db=db, lat=point.latitude, long=point.longitude, db_obj=ue
            )

            logging.info("The current cell is %d", cell_now)
            if cell_now and ue.Cell_id != cell_now.id:
                handovers[ue.supi].append(cell_now.id)
                ue.Cell_id = cell_now.id
                crud.ue.update(
                    db=db,
                    db_obj=ue,
                    obj_in={"Cell_id": ue.Cell_id},
                )

            await location_notification(
                ue, ue.Cell_id, cell_now.id if cell_now else None
            )

            await asyncio.sleep(1)


async def location_notification(
    ue: UE, old_cell_id: Optional[int] = None, current_cell_id: Optional[int] = None
):
    db_mongo = client.fastapi

    subscriptions = list(
        db_mongo["MonitoringEvent"].find({"supi": str(ue.supi)}, {"subscription": True})
    )

    for doc in subscriptions:
        doc_id = doc.get("_id")
        sub = doc["subscription"]
        sub_validate_time = tools.check_expiration_time(
            expire_time=sub.get("monitorExpireTime")
        )

        sub_validate_number_of_reports = tools.check_numberOfReports(
            sub.get("maximumNumberOfReports")
        )

        if not sub_validate_time or not sub_validate_number_of_reports:
            crud_mongo.delete_by_uuid(db_mongo, "MonitoringEvent", doc_id)
            continue

        monitoringType = sub["monitoringType"]

        if monitoringType == MonitoringType.LOCATION_REPORTING:
            asyncio.create_task(handle_location_report_callback(sub, ue, doc_id))

        elif monitoringType == MonitoringType.LOSS_OF_CONNECTIVITY:
            asyncio.create_task(
                handle_loss_connectivity_callback(
                    sub, ue, doc_id, old_cell_id, current_cell_id
                )
            )

        elif monitoringType == MonitoringType.UE_REACHABILITY:
            asyncio.create_task(
                handle_ue_reachability_callback(
                    sub, ue, doc_id, old_cell_id, current_cell_id
                )
            )


@router.post("/update_location/{supi}", status_code=204)
def update_location(
    *,
    supi: str = Path(...),
    new_location: Point,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    with db_context() as db:
        ue = crud.ue.get_supi(db, supi)

        if not ue:
            raise HTTPException(
                status_code=404,
                detail="No device found",
            )

        ue = crud.ue.update_coordinates(
            db,
            lat=new_location.point.lat,
            long=new_location.point.lon,
            db_obj=ue,
        )

    background_tasks.add_task(location_notification, ue)

    return {"msg": "Location updated"}


@router.post("/start-loop", status_code=200)
def initiate_movement(
    *,
    msg: Msg,
    current_user: models.User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Start the loop.
    """
    if msg.supi in moving_devices:
        raise HTTPException(
            status_code=409,
            detail=f"There is a thread already running for this supi:{msg.supi}",
        )

    moving_devices[msg.supi] = current_user.id
    background_tasks.add_task(movement_loop, msg.supi, current_user)

    return {"msg": "Loop started"}


@router.post("/stop-loop", status_code=200)
def terminate_movement(
    *,
    msg: Msg,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Stop the loop.
    """
    try:
        moving_devices.pop(msg.supi)
        return {"msg": "Loop ended"}
    except KeyError as ke:
        logging.warning("Key Not Found in Moving Devices Dictionary:", ke)
        raise HTTPException(
            status_code=409,
            detail="There is no generator running for this SUPI",
        )


@router.get("/state-loop/{supi}", status_code=200)
def state_movement(
    *,
    supi: str = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the state
    """
    return {"running": retrieve_ue_state(supi, current_user.id)}


@router.get("/state-ues", status_code=200)
def state_ues(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get the state
    """
    return crud.ue.get_multi_by_owner(db, owner_id=current_user.id)


# Functions
def retrieve_ue_state(supi: str, user_id: int) -> bool:
    return moving_devices.get(supi) is not None


def retrieve_ue(supi: str, db: Session) -> Optional[UE]:
    if moving_devices.get(supi):
        return crud.ue.get_supi(db, supi)

    return None


def retrieve_ue_distances(supi: str, user_id: int, db: Session) -> dict:
    ue = crud.ue.get_supi(db, supi)
    if ue is None:
        return {}

    cells = crud.cell.get_multi_by_owner(db=db, owner_id=user_id)

    _, distances = check_distance(ue.latitude, ue.longitude, cells)
    return distances


def retrieve_ue_path_losses(supi: str, id, db: Session) -> dict:
    ue = crud.ue.get_supi(db, supi=supi)
    if ue is None:
        return {}

    cells = crud.cell.get_multi_by_owner(db, owner_id=id)

    return check_path_loss(ue.latitude, ue.longitude, jsonable_encoder(cells))


def retrieve_ue_rsrps(supi: str, id, db: Session) -> dict:
    ue = crud.ue.get_supi(db, supi=supi)
    if ue is None:
        return {}

    cells = crud.cell.get_multi_by_owner(db, owner_id=id)

    return check_rsrp(ue.latitude, ue.longitude, jsonable_encoder(cells))


def retrieve_ue_handovers(supi: str) -> list:
    result = handovers.get(supi)
    return result if result is not None else []
