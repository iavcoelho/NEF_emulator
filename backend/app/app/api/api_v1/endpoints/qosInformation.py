from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.orm.session import Session
from app.db.session import client
from app import models
from app.api import deps
from app.core.config import QoSProfile, qosSettings
from app.crud import crud_mongo, user, gnb

def qos_reference_match(qos_reference: str) -> Optional[QoSProfile]:
    return qosSettings.get_qos_profile(qos_reference)

router = APIRouter()

@router.get("/qosCharacteristics")
def read_qos_characteristics() -> List[QoSProfile]:
    """
    Get the available QoS Characteristics
    """
    return qosSettings.get_all_profiles()
    

@router.get("/qosProfiles/{gNB_id}")
def read_qos_active_profiles(
    *,
    gNB_id: str = Path(..., title="The ID of the gNB", example="AAAAA1"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get the available QoS Characteristics
    """
    db_mongo = client.fastapi

    gNB = gnb.get_gNB_id(db=db, id=gNB_id)
    if not gNB:
        raise HTTPException(status_code=404, detail="gNB not found")
    if not user.is_superuser(current_user) and (gNB.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    retrieved_doc = crud_mongo.read_all_gNB_profiles(db_mongo, 'QoSProfile', gNB.gNB_id)

    if not retrieved_doc:
        raise HTTPException(status_code=404, detail=f"No QoS profiles for gNB {gNB.gNB_id}")
    else:
        return retrieved_doc



@router.get("/qosRules/{supi}", deprecated=True)
def read_qos_active_rules(
    *,
    supi: str = Path(..., title="The subscription unique permanent identifier (SUPI) of the UE", example="202010000000001"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    """
    Get the available QoS Characteristics
    """
    pass




    
    
    
