import logging
from math import exp
import time
from datetime import date, datetime
from typing import Optional, Union
from app.crud import crud_mongo


def check_expiration_time(expire_time: Union[datetime, str]) -> bool:
    if not expire_time:
        return True

    if isinstance(expire_time, str):
        expire_time = datetime.fromisoformat(expire_time)

    now = datetime.now(expire_time.tzinfo) if expire_time.tzinfo else datetime.now()

    return now < expire_time


def check_numberOfReports(maximum_number_of_reports: Optional[int]) -> bool:
    if maximum_number_of_reports is None:
        return True

    if maximum_number_of_reports < 0:
        logging.warning("Subscription has expired (maximum number of reports)")
        return False

    return True
