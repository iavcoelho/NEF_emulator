import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.database import Database
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.crud import crud_mongo, user, ue
from app.db.session import client
from .utils import add_notifications

router = APIRouter()
#TODO: db
db_collection= 'BdtManagement'

@router.get("/{scsAsId}/subscriptions", response_model=List[schemas.Bdt])
def read_active_subscriptions(
    *,
    scsAsId: str = Path(..., title="The ID of the Netapp that creates a subscription", example="myNetapp"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    """
    Get subscription by id
    """
    db_mongo = client.fastapi
    print(current_user)
    retrieved_docs = crud_mongo.read_all(db_mongo, db_collection, current_user.id)

    #Check if there are any active subscriptions
    if not retrieved_docs:
        raise HTTPException(status_code=404, detail="There are no active subscriptions")
    
    http_response = JSONResponse(content=retrieved_docs, status_code=200)
    add_notifications(http_request, http_response, False)
    return http_response

#Callback 

# bdt_callback_router = APIRouter()

# @bdt_callback_router.post("{$request.body.notificationDestination}",response_class=Response)
# def bdt_notification(body: schemas.ExNotification):
#     pass

# , callbacks=bdt_callback_router.routes
@router.post("/{scsAsId}/subscriptions", responses={201: {"model" : schemas.Bdt}})
def create_subscription(
    *,
    scsAsId: str = Path(..., title="The ID of the Netapp that creates a subscription", example="myNetapp"),
    db: Session = Depends(deps.get_db),
    item_in: schemas.BdtCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    
    db_mongo = client.fastapi
    json_data = jsonable_encoder(item_in)
    json_data.update({'owner_id' : current_user.id})

    inserted_doc = crud_mongo.create(db_mongo, db_collection, json_data)

    #Create the reference resource and location header
    link = str(http_request.url) + '/' + str(inserted_doc.inserted_id)
    response_header = {"location" : link}

    #Update the subscription with the new resource (link) and return the response (+response header)
    crud_mongo.update_new_field(db_mongo, db_collection, inserted_doc.inserted_id, {"link" : link})
    
    #Retrieve the updated document | UpdateResult is not a dict
    updated_doc = crud_mongo.read_uuid(db_mongo, db_collection, inserted_doc.inserted_id)

    updated_doc.pop("owner_id") #Remove owner_id from the response

    http_response = JSONResponse(content=updated_doc, status_code=201, headers=response_header)
    add_notifications(http_request, http_response, False)

    return http_response