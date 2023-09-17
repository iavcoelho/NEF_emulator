from pydantic import BaseModel, constr
# from .utils import ExtraBaseModel

class Msg(BaseModel):
    supi: constr(regex=r'^[0-9]{15,16}$')

class SinusoidalParameters(BaseModel):
    amplitude: float
    frequency: float
    phase: float
    offset: float