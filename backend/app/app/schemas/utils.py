from pydantic import BaseModel, Extra

class ExtraBaseModel(BaseModel):

    class Config:
        extra = Extra.forbid
