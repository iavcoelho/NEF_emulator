from typing import List
from abc import ABC, abstractmethod

from app.crud.crud_UE import UE
from app.core.config import QoSProfile
from app.schemas.afSessionWithQos import AsSessionWithQoSSubscription


class AfSessionWithQosInterface(ABC):
    @abstractmethod
    async def change_qos(
        self, subscription: AsSessionWithQoSSubscription, ues: List[UE], qos: QoSProfile
    ) -> None:
        pass

    @abstractmethod
    async def revert_qos(
        self, subscription: AsSessionWithQoSSubscription, ues: List[UE]
    ) -> None:
        pass
