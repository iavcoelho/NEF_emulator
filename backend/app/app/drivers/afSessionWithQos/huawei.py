import logging
from typing import List, Optional

import httpx

from app.crud.crud_UE import UE
from app.core.config import QoSProfile
from app.schemas.afSessionWithQos import AsSessionWithQoSSubscription
from app.interfaces.afSessionWithQos import AfSessionWithQosInterface


class HuaweiAfSessionWithQos(AfSessionWithQosInterface):
    def __init__(
        self,
        slice_manager_api_url: str,
        default_ambrup: int,
        default_ambrdl: int,
        api_user: str,
        api_password: str,
    ) -> None:
        super().__init__()

        self.httpx_client = httpx.AsyncClient(
            base_url=slice_manager_api_url,
            auth=httpx.BasicAuth(username=api_user, password=api_password),
            # The API is slow to respond, so disable timeouts
            timeout=None
        )
        self.default_ambrup = default_ambrup
        self.default_ambrdl = default_ambrdl

    async def _change_ue_qos(
        self, ue: UE, slice: str, ambrup: Optional[int], ambrdl: Optional[int]
    ) -> None:
        payload: dict = {
            "IMSI": ue.supi,
            "numIMSIs": 1,
            "slice": slice,
            "AMDATA": True,
            "AMBRUP": ambrup,
            "AMBRDW": ambrdl,
        }

        res = await self.httpx_client.get(f"/UE/{ue.supi}/get_IMSI")

        if res.is_success:
            logging.debug("Patching UE state")
            res = await self.httpx_client.patch("/UE/patch", json=payload)
        elif res.status_code == 404:
            logging.debug("Creating new UE state")
            res = await self.httpx_client.post("/UE/post", json=payload)
        else:
            raise Exception(
                f"Error while getting UE status in Huawei Core for {ue.supi} (status code: {res.status_code}): {res.text}"
            )

        if res.is_success:
            logging.debug(f"Provisioned QoS in Huawei Core for {ue.supi}")
            return

        raise Exception(
            f"Error while changing QoS in Huawei Core for {ue.supi} (status code: {res.status_code}): {res.text}"
        )

    async def change_qos(
        self, subscription: AsSessionWithQoSSubscription, ues: List[UE], qos: QoSProfile
    ) -> None:
        # The Slice Manager API expects the value to be in Kbps but the
        # interface works with bps so we need to divide by 1000 rounding up
        ambrup = qos.uplinkBitRate
        if ambrup is not None:
            ambrup = (ambrup + 999) // 1000

        ambrdl = qos.downlinkBitRate
        if ambrdl is not None:
            ambrdl = (ambrdl + 999) // 1000


        for ue in ues:
            await self._change_ue_qos(
                ue, subscription.dnn or ue.dnn, ambrup, ambrdl
            )

    async def revert_qos(
        self, subscription: AsSessionWithQoSSubscription, ues: List[UE]
    ) -> None:
        for ue in ues:
            await self._change_ue_qos(
                ue, subscription.dnn or ue.dnn, self.default_ambrup, self.default_ambrdl
            )
