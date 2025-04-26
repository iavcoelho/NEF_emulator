from typing import Optional, Annotated
from enum import Enum
from pydantic import BaseModel, IPvAnyAddress, Field, constr, confloat

from app.schemas.commonData import Msisdn
from typing_extensions import Annotated

class Speed(str, Enum):
    stationary = "STATIONARY"
    low = "LOW"
    high = "HIGH"

# Shared properties
class UEBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ip_address_v4: Optional[IPvAnyAddress] = Field(default='10.0.0.0', description="String identifying an Ipv4 address")    
    ip_address_v6: Optional[IPvAnyAddress] = Field(default="0:0:0:0:0:0:0:0", description="String identifying an Ipv6 address. Default value ::1/128 (loopback)")
    mac_address: constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$') = '22-00-00-00-00-00'
    msisdn: Annotated[Optional[Msisdn], Field(description="String identifying a phone number (MSISDN)")] = "2020100000000"
    dnn: Optional[str] = Field(default='province1.mnc01.mcc202.gprs', description="String identifying the Data Network Name (i.e., Access Point Name in 4G). For more information check clause 9A of 3GPP TS 23.003")
    mcc: Optional[int] = Field(default=202, description="Mobile Country Code (MCC) part of the Public Land Mobile Network (PLMN), comprising 3 digits, as defined in clause 9.3.3.5 of 3GPP TS 38.413")
    mnc: Optional[int] = Field(default=1, description="Mobile Network Code (MNC) part of the Public Land Mobile Network (PLMN), comprising 2 or 3 digits, as defined in clause 9.3.3.5 of 3GPP TS 38.413")
    external_identifier: Optional[str] = Field("123456789@domain.com", description="Globally unique identifier containing a Domain Identifier and a Local Identifier. \<Local Identifier\>@\<Domain Identifier\>")
    speed: Speed = Field(default="LOW", description="This value describes UE's speed. Possible values are \"STATIONARY\" (e.g, IoT device), \"LOW(e.g, pedestrian)\" and \"HIGH (e.g., vehicle)\"")

class UECreate(UEBase):
    supi: constr(regex=r'^[0-9]{15,16}$') = Field(default="202010000000000", description= """String identifying a Supi that shall contain either an IMSI, a network specific identifier, a Global Cable Identifier (GCI) or a Global Line Identifier (GLI) as specified in clause 2.2A of 3GPP TS 23.003. 
                                                                                             In the current version (v1.1.0) only IMSI is supported""")

class UEUpdate(UEBase):
    pass

class ue_path(BaseModel):
    supi: constr(regex=r'^[0-9]{15,16}$') = Field(default="202010000000000", description= """String identifying a Supi that shall contain either an IMSI, a network specific identifier, a Global Cable Identifier (GCI) or a Global Line Identifier (GLI) as specified in clause 2.2A of 3GPP TS 23.003.                                                                                                                                                                             In the current version (v1.1.0) only IMSI is supported""")    
    path: int

# Properties to return to client
class UE(UEBase):
    supi: constr(regex=r'^[0-9]{15,16}$') = Field(default="202010000000000", description= """String identifying a Supi that shall contain either an IMSI, a network specific identifier, a Global Cable Identifier (GCI) or a Global Line Identifier (GLI) as specified in clause 2.2A of 3GPP TS 23.003.                                                                                          
                                                                                      In the current version (v1.1.0) only IMSI is supported""")
    latitude: Optional[confloat(ge=-90, le=90)] 
    longitude: Optional[confloat(ge=-180, le=180)]                                                                                      
    path_id: Optional[int]
    gNB_id: Optional[int]
    Cell_id: Optional[int]
    
    class Config:
        orm_mode = True

# Properties to return to client with cell id hex 
class UEhex(UE):
    cell_id_hex: Optional[str]
    id: int
