import logging
import asyncio
from typing import Optional
from app import crud

from app.core.notification_responder import notification_responder
from app.models.UE import UE
from app.db.session import client
from app.schemas.monitoringevent import (
    GeographicalCoordinates,
    LocationInfo,
    MonitoringEventReport,
    MonitoringNotification,
    MonitoringType,
    ReachabilityType,
    Point,
    SupportedGADShapes,
)

from app.api.deps import db_context


def update_maximum_reports(sub, id):
    db_mongo = client.fastapi
    if sub.get("maximumNumberOfReports") is not None:
        db_mongo["MonitoringEvent"].find_one_and_update(
            {"_id": id},
            {"$inc": {"subscription.maximumNumberOfReports": -1}},
        )


async def handle_location_report_callback(location_reporting_sub, ue: UE, doc_id):
    logging.info(
        "Attempting to send the callback to %d",
        location_reporting_sub.get("notificationDestination"),
    )

    report = MonitoringEventReport(
        externalId=ue.external_identifier,
        monitoringType=MonitoringType.LOCATION_REPORTING,
        locationInfo=LocationInfo(
            geographicArea=Point(
                shape=SupportedGADShapes.POINT,
                point=GeographicalCoordinates(
                    lat=ue.latitude,
                    lon=ue.longitude,
                ),
            ),
        ),
    )

    if ue.Cell_id is not None and report.locationInfo is not None:
        report.locationInfo.cellId = ue.Cell.cell_id

    notification = MonitoringNotification(
        subscription=location_reporting_sub.get("self"),
        monitoringEventReports=[report],
    )

    try:
        await notification_responder.send_notification(
            location_reporting_sub.get("notificationDestination"), notification
        )
        update_maximum_reports(location_reporting_sub, doc_id)
    except Exception as ex:
        raise ex


async def handle_loss_connectivity_callback(
    loss_of_connectivity_sub,
    ue: UE,
    doc_id,
    old_cell_id: Optional[str],
    current_cell_id: Optional[str],
):
    if old_cell_id is None or current_cell_id is not None:
        return

    if loss_of_connectivity_sub.get("maximumDetectionTime") is not None:
        await asyncio.sleep(loss_of_connectivity_sub.get("maximumDetectionTime"))
        with db_context() as db:
            new_ue = crud.ue.get_supi(db=db, supi=ue.supi)
            if new_ue is None or new_ue.Cell_id is not None:
                return

    notification = MonitoringNotification(
        subscription=loss_of_connectivity_sub.get("self"),
        monitoringEventReports=[
            MonitoringEventReport(
                externalId=ue.external_identifier,
                monitoringType=MonitoringType.LOSS_OF_CONNECTIVITY,
                lossOfConnectReason=2,
            )
        ],
    )

    try:
        await notification_responder.send_notification(
            loss_of_connectivity_sub.get("notificationDestination"),
            notification,
        )

        update_maximum_reports(loss_of_connectivity_sub, doc_id)
    except Exception as ex:
        raise ex


async def handle_ue_reachability_callback(
    subscription,
    ue: UE,
    doc_id,
    old_cell_id: Optional[str],
    current_cell_id: Optional[str],
):
    if current_cell_id is None or old_cell_id is not None:
        return

    return await send_ue_reachability_callback(subscription, ue, doc_id)


async def send_ue_reachability_callback(subscription, ue: UE, doc_id):
    notification = MonitoringNotification(
        subscription=subscription.get("self"),
        monitoringEventReports=[
            MonitoringEventReport(
                externalId=ue.external_identifier,
                monitoringType=MonitoringType.UE_REACHABILITY,
                reachabilityType=ReachabilityType.DATA,
            )
        ],
    )

    try:
        await notification_responder.send_notification(
            subscription.get("notificationDestination"), notification
        )
        update_maximum_reports(subscription, doc_id)
    except Exception as ex:
        raise ex
