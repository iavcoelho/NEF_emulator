from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app import crud, models
from app.api import deps
from app.api.api_v1.endpoints.ue_movement import (
    retrieve_ue,
    retrieve_ue_distances,
    retrieve_ue_path_losses,
    retrieve_ue_rsrps,
    retrieve_ue_handovers,
)
from .utils import ReportLogging

router = APIRouter()
router.route_class = ReportLogging


@router.get("/{supi}/serving_cell")
def read_UE_serving_cell(
    *,
    db: Session = Depends(deps.get_db),
    supi: str = Path(..., description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    ue = retrieve_ue(supi)
    if ue is None:
        raise HTTPException(status_code=400, detail="The emulation needs to be ongoing")

    log = {
        "latitude": ue.latitude,
        "longitude": ue.longitude,
        "UE_id": ue.name,
        "S-PCI": ue.Cell_id,
    }

    return log


@router.get("/{supi}/distances")
def read_UE_distances(
    *,
    db: Session = Depends(deps.get_db),
    supi: str = Path(..., description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if retrieve_ue(supi) == None:
        raise HTTPException(status_code=400, detail="The emulation needs to be ongoing")

    return retrieve_ue_distances(supi, current_user.id)


@router.get("/{supi}/path_losses")
def read_UE_losses(
    *,
    db: Session = Depends(deps.get_db),
    supi: str = Path(..., description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if retrieve_ue(supi) == None:
        raise HTTPException(status_code=400, detail="The emulation needs to be ongoing")

    return retrieve_ue_path_losses(supi, current_user.id)


@router.get("/{supi}/rsrps")
def read_UE_rsrps(
    *,
    db: Session = Depends(deps.get_db),
    supi: str = Path(..., description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if retrieve_ue(supi) == None:
        raise HTTPException(status_code=400, detail="The emulation needs to be ongoing")

    return retrieve_ue_rsrps(supi, current_user.id)


@router.get("/{supi}/handovers")
def read_UE_handovers(
    *,
    db: Session = Depends(deps.get_db),
    supi: str = Path(..., description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    print(UE)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if retrieve_ue(supi) == None:
        raise HTTPException(status_code=400, detail="The emulation needs to be ongoing")

    return retrieve_ue_handovers(supi)
