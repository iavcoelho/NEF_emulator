import logging
from typing import List

from app.crud.crud_UE import UE
from app.core.config import QoSProfile
from app.schemas.afSessionWithQos import AsSessionWithQoSSubscription
from app.interfaces.afSessionWithQos import AfSessionWithQosInterface


class NoopAfSessionWithQos(AfSessionWithQosInterface):
    async def change_qos(
        self, subscription: AsSessionWithQoSSubscription, ues: List[UE], qos: QoSProfile
    ) -> None:
        logging.info(
            f"Would update QoS to {qos} for the following UEs: {list(map(lambda ue: ue.supi, ues))}"
        )

    async def revert_qos(
        self, subscription: AsSessionWithQoSSubscription, ues: List[UE]
    ) -> None:
        logging.info(
            f"Would revert QoS for the following UEs: {list(map(lambda ue: ue.supi, ues))}"
        )
