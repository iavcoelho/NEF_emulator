import json
import logging
from re import sub
import requests
import asyncio
from typing import Optional, List
from app import crud

from app.core.notification_responder import notification_responder
from app.crud.crud_mongo import update
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
        sub["maximumNumberOfReports"] = sub["maximumNumberOfReports"] - 1
        db_mongo["MonitoringEvent"].find_one_and_update(
            {"_id": id},
            {"$set": {"subscription": sub}},
        )


async def handle_location_report_callback(location_reporting_sub, ue: UE, doc_id):
    logging.info(
        "Attempting to send the callback to %d",
        location_reporting_sub.get("notificationDestination"),
    )

    notification = MonitoringNotification(
        subscription=location_reporting_sub.get("self"),
        monitoringEventReports=[
            MonitoringEventReport(
                externalId=ue.external_identifier,
                monitoringType=MonitoringType.LOCATION_REPORTING,
                locationInfo=LocationInfo(
                    cellId=ue.Cell_id,
                    enodeBId=None,
                    geographicArea=Point(
                        shape=SupportedGADShapes.POINT,
                        point=GeographicalCoordinates(
                            lat=ue.latitude,
                            lon=ue.longitude,
                        ),
                    ),
                ),
            )
        ],
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
    old_cell_id: Optional[int],
    current_cell_id: Optional[int],
):
    if not old_cell_id or current_cell_id:
        return

    await asyncio.sleep(loss_of_connectivity_sub.get("maximumDurationTime"))
    with db_context() as db:
        new_ue = crud.ue.get_supi(db=db, supi=ue.supi)
        if not new_ue or new_ue.Cell_id:
            return

        notification = MonitoringNotification(
            subscription=loss_of_connectivity_sub.get("link"),
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

    logging.info("There was an attempt at calling the connectivity callback")


async def handle_ue_reachability_callback(
    subscription,
    ue: UE,
    doc_id,
    old_cell_id: Optional[int],
    current_cell_id: Optional[int],
):
    if not current_cell_id or old_cell_id:
        return

    notification = MonitoringNotification(
        subscription=subscription.get("link"),
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
