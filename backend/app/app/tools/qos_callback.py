import requests
import logging

from fastapi.encoders import jsonable_encoder

from app.crud import ue
from app.db.session import SessionLocal
from app.api.api_v1.endpoints.afSessionWithQoS import extract_qos_profile
from app.schemas.afSessionWithQos import (
    AsSessionWithQoSSubscription,
    UserPlaneEvent,
    UserPlaneEventReport,
    UserPlaneNotificationData,
)


def qos_callback(callbackurl, resource, qos_status: UserPlaneEvent):
    url = callbackurl

    payload = jsonable_encoder(
        UserPlaneNotificationData(
            transaction=resource, eventReports=[UserPlaneEventReport(event=qos_status)]
        ).dict(exclude_unset=True)
    )

    # Timeout values according to https://docs.python-requests.org/en/master/user/advanced/#timeouts
    # First value of the tuple "3.05" corresponds to connect and second "27" to read timeouts
    # (i.e., connect timeout means that the server is unreachable and read that the server is reachable but the client does not receive a response within 27 seconds)

    response = requests.post(url, json=payload, timeout=(3.05, 27))

    return response


def qos_notification_control(
    doc: AsSessionWithQoSSubscription, ues: dict, current_ue: dict
):
    number_of_ues_in_cell = ues_in_cell(ues, current_ue)

    if number_of_ues_in_cell > 1:
        gbr_status = UserPlaneEvent.QOS_NOT_GUARANTEED
    else:
        gbr_status = UserPlaneEvent.QOS_GUARANTEED

    qos_standardized = extract_qos_profile(doc)

    try:
        # logging.critical("Before response")
        response = qos_callback(doc.notificationDestination, doc.self, gbr_status)
        logging.critical(f"Response from {doc.notificationDestination}: {response}")
    except requests.exceptions.Timeout as ex:
        logging.critical("Failed to send the callback request")
        logging.critical(ex)
    except requests.exceptions.TooManyRedirects as ex:
        logging.critical("Failed to send the callback request")
        logging.critical(ex)
    except requests.exceptions.RequestException as ex:
        logging.critical("Failed to send the callback request")
        logging.critical(ex)

    return


def ues_in_cell(ues: dict, current_ue: dict):
    ues_connected = 0

    # Find running UEs belong in the same cell
    for single_ue in ues:
        if ues[single_ue]["Cell_id"] == current_ue["Cell_id"]:
            ues_connected += 1

    # Find stationary UEs belong in the same cell
    db = SessionLocal()

    ues_list = ue.get_by_Cell(db=db, cell_id=current_ue["Cell_id"])

    for ue_in_db in ues_list:
        # This means that we are searching only for ues that are not running
        # In db the last known location (cell_id) is valid only for UEs that are not running
        if jsonable_encoder(ue_in_db).get("supi") not in ues:
            ues_connected += 1

    db.close()

    return ues_connected
