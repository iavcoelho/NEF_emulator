from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session # this will allow you to declare the type of the db parameters and have better type checks and completion in your functions.

from app.crud.base import CRUDBase
from app.models.monitoringevent import Monitoring
from app.schemas.monitoringevent import MonitoringEventSubscription
from app.schemas.UE import UECreate, UEUpdate


class CRUD_Monitoring(CRUDBase[Monitoring, MonitoringEventSubscription, MonitoringEventSubscription]):
    def create_with_owner(
        self, db: Session, *, obj_in: MonitoringEventSubscription, owner_id: int
    ) -> Monitoring:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Monitoring]:
        return (
            db.query(self.model)
            .filter(Monitoring.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_sub_ipv4(self, db: Session, ipv4: str) -> Monitoring:
        return db.query(self.model).filter(Monitoring.ipv4Addr == ipv4).first()

monitoring = CRUD_Monitoring(Monitoring)
