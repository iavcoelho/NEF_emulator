import logging

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session

from app import models, schemas, crud
from app.api import deps
from app.api.api_v1.endpoints.paths import get_random_point
from app.api.api_v1.endpoints.ue_movement import retrieve_ue_state

router = APIRouter()

@router.post("/import/scenario")
def create_scenario(
    scenario_in: schemas.scenario,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user), 
) -> Any:
    """
    Export the scenario
    """
    err = {}
    
    gNBs = scenario_in.gNBs
    cells = scenario_in.cells
    ues = scenario_in.UEs
    paths = scenario_in.paths
    ue_path_association = scenario_in.ue_path_association

    db.execute('TRUNCATE TABLE cell, gnb, monitoring, path, points, ue RESTART IDENTITY')
    
    for gNB_in in gNBs:
        gNB = crud.gnb.get_gNB_id(db=db, id=gNB_in.gNB_id)
        if gNB:
            print(f"ERROR: gNB with id {gNB_in.gNB_id} already exists")
            err.update({f"{gNB_in.name}" : f"ERROR: gNB with id {gNB_in.gNB_id} already exists"})
        else:
            gNB = crud.gnb.create_with_owner(db=db, obj_in=gNB_in, owner_id=current_user.id)

    for cell_in in cells:
        cell = crud.cell.get_Cell_id(db=db, id=cell_in.cell_id)
        if cell:
            print(f"ERROR: Cell with id {cell_in.cell_id} already exists")
            err.update({f"{cell_in.name}" : f"ERROR: Cell with id {cell_in.cell_id} already exists"})
            crud.cell.remove_all_by_owner(db=db, owner_id=current_user.id)
        else:
            cell = crud.cell.create_with_owner(db=db, obj_in=cell_in, owner_id=current_user.id)

    for ue_in in ues:
        ue = crud.ue.get_supi(db=db, supi=ue_in.supi)
        if ue:
            print(f"ERROR: UE with supi {ue_in.supi} already exists")
            err.update({f"{ue.name}" : f"ERROR: UE with supi {ue_in.supi} already exists"})
        else:
            ue = crud.ue.create_with_owner(db=db, obj_in=ue_in, owner_id=current_user.id)

    for path_in in paths:
        path_old_id = path_in.id

        path = crud.path.get_description(db=db, description = path_in.description)
        if path:
            print(f"ERROR: Path with description \'{path_in.description}\' already exists")
            err.update({f"{path_in.description}" : f"ERROR: Path with description \'{path_in.description}\' already exists"})
        else:
            path = crud.path.create_with_owner(db=db, obj_in=path_in, owner_id=current_user.id)
            crud.points.create(db=db, obj_in=path_in, path_id=path.id) 
            
            for ue_path in ue_path_association:
                if retrieve_ue_state(ue_path.supi, current_user.id):
                    err.update(f"UE with SUPI {ue_path.supi} is currently moving. You are not allowed to edit UE's path while it's moving")
                else:
                    #Assign the coordinates
                    UE = crud.ue.get_supi(db=db, supi=ue_path.supi)
                    json_data = jsonable_encoder(UE)
                    
                    #Check if the old path id or the new one is associated with one or more UEs store in ue_path_association dictionary
                    #If not then add path_id 0 on UE's table 
                    print(f'Ue_path_association {ue_path.path}')
                    print(f'Path old id: {path_old_id}')
                    if ue_path.path == path_old_id:
                        print(f'New path id {path.id}')
                        json_data['path_id'] = path.id
                        random_point = get_random_point(db, path.id)
                        json_data['latitude'] = random_point.get('latitude')
                        json_data['longitude'] = random_point.get('longitude')
                    
                    crud.ue.update(db=db, db_obj=UE, obj_in=json_data)
    
    if bool(err) == True:
        raise HTTPException(status_code=409, detail=err)
    else:
        return ""


@router.get("/export/scenario", response_model=schemas.scenario)
def get_scenario(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Export the scenario
    """
    gNBs = crud.gnb.get_multi_by_owner(db=db, owner_id=current_user.id, skip=0, limit=100)
    Cells = crud.cell.get_multi_by_owner(db=db, owner_id=current_user.id, skip=0, limit=100)
    UEs = crud.ue.get_multi_by_owner(db=db, owner_id=current_user.id, skip=0, limit=100)
    paths = crud.path.get_multi_by_owner(db=db, owner_id=current_user.id, skip=0, limit=100)

    
    json_gNBs= jsonable_encoder(gNBs)
    json_Cells= jsonable_encoder(Cells)
    json_UEs= jsonable_encoder(UEs)
    json_path = jsonable_encoder(paths)
    ue_path_association = []

    for item_json in json_path:
        for path in paths:
            if path.id == item_json.get('id'):
                item_json["start_point"] = {}
                item_json["end_point"] = {}
                item_json["start_point"]["latitude"] = path.start_lat
                item_json["start_point"]["longitude"] = path.start_long
                item_json["end_point"]["latitude"] = path.end_lat
                item_json["end_point"]["longitude"] = path.end_long
                item_json["id"] = path.id
                points = crud.points.get_points(db=db, path_id=path.id)
                item_json["points"] = []
                for obj in jsonable_encoder(points):
                    item_json["points"].append({'latitude' : obj.get('latitude'), 'longitude' : obj.get('longitude')})

    for ue in UEs:
        if ue.path_id:
            json_ue_path_association = {}
            json_ue_path_association["supi"] = ue.supi
            json_ue_path_association["path"] = ue.path_id
            ue_path_association.append(json_ue_path_association)
         
    logging.critical(ue_path_association)
    logging.critical(json_UEs)

    export_json = {
        "gNBs" : json_gNBs,
        "cells" : json_Cells,
        "UEs" : json_UEs,
        "paths" : json_path,
        "ue_path_association" : ue_path_association
    }

    return export_json
