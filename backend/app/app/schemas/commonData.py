from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress, AnyHttpUrl, constr
from enum import Enum


#Defined with other classes, without making a new class type
#Link - AnyHttpUrl
#DateTime - datetime
#Dnn - str -> example: province1.mnc01.mcc202.gprs
#ExternalId - str -> example: 123456789@domain.com
#Msisdn - str -> example: 918369110173
#ExternalGroupId - str -> example: Group1@domain.com
#IpAddr - IPvAnyAddress
#MacAddr48 - constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$')
#DurationSec - int -> ge = 0
#DayOfWeek ???
#TimeOfDay ???
#DurationSecRm ???
#DurationSecRo ???

#TODO:
#29.571
#SupportedFeatures
#Dnai
#TypeAllocationCode
#Gpsi ---  '^(msisdn-[0-9]{5,15}|extid-.+@.+|.+)$'
#Uri
#ApplicationId - str --- String providing an application identifier. 
#BitRate - constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')
#Uinteger - int -> ge = 0
#Float - float
#SamplingRatio - int -> ge = 1, le = 100 --- expressed in percent
#PacketDelBudget - int -> ge = 1 --- expressed in milliseconds.
#PacketLossRate - int -> ge = 0, le = 1000 --- expressed in tenth of percent
#Ecgi
#Ncgi
#GlobalRanNodeId
#Tai
#EutraCellId - constr(regex=r'^[A-Fa-f0-9]{7}$')
#Nid - constr(regex=r'^[A-Fa-f0-9]{11}$')
#NrCellId - constr(regex=r'^[A-Fa-f0-9]{9}$')
#N3IwfId - constr(regex=r'^[A-Fa-f0-9]+$')
#NgeNbId - constr(regex=r'^(MacroNGeNB-[A-Fa-f0-9]{5}|LMacroNGeNB-[A-Fa-f0-9]{6}|SMacroNGeNB-[A-Fa-f0-9]{5})$')
#WAgfId - constr(regex=r'^[A-Fa-f0-9]+$')
#TngfId - constr(regex=r'^[A-Fa-f0-9]+$')
#ENbId - constr(regex=r'^(MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5}|HomeeNB-[A-Fa-f0-9]{7})$')
#Tac - constr(regex=r'(^[A-Fa-f0-9]{4}$)|(^[A-Fa-f0-9]{6}$)')
#PduSessionId - int -> ge = 0, le = 255
#UserLocation
#Supi


#TODO:
#29.122
#Volume -- int -> ge = 0 ---  Unsigned integer identifying a volume in units of bytes.
#WebsockNotifConfig
#LocationArea
#LocationArea5G
#ConfigResult
#TimeWindow
#FlowInfo
#TimeOfDay - time

#29.514
#FlowDescription -> str --- defines a packet filter of an IP flow

class FlowInfo(BaseModel):
    """Represents IP flow information."""
    flowId: int = Field(None, description="Indicates the IP flow identifier.")
    flowDescriptions: List[str] = Field(None, description="Indicates the packet filters of the IP flow. Refer to clause 5.3.8 of 3GPP TS 29.214 for encoding. It shall contain UL and/or DL IP flow description.", min_items=1, max_items=2)

class TimeWindow(BaseModel):
    """Represents a time window identified by a start time and a stop time."""
    startTime: datetime
    stopTime: datetime

class Snssai(BaseModel):
    sst: int = Field(default=1, description="Unsigned integer representing the Slice/Service Type. Value 0 to 127 correspond to the standardized SST range. Value 128 to 255 correspond to the Operator-specific range.", ge=0, le=255)
    sd: Optional[constr(regex=r'^[0-9a-fA-F]{6}$')] = Field(default='000001', description="This value respresents the Slice Differentiator, in hexadecimal representation.")

class UsageThreshold(BaseModel):
    duration: int = Field(None, description="A period of time in units of seconds", ge=0)
    totalVolume: int = Field(None, description="A volume in units of bytes", ge=0)
    downlinkVolume: int = Field(None, description="A volume in units of bytes", ge=0)
    uplinkVolume: int = Field(None, description="A volume in units of bytes", ge=0)

#TS 29.571
class PlmnId(BaseModel):
    mcc: int
    mnc: int

#TS 29.571
class Ecgi(BaseModel):
    """Contains the ECGI (E-UTRAN Cell Global Identity), as described in 3GPP 23.003"""
    plmnId: PlmnId
    eutraCellId: constr(regex=r'^[A-Fa-f0-9]{7}$')
    nid: Optional[constr(regex=r'^[A-Fa-f0-9]{11}$')]


#TS 29.571
class Ncgi(BaseModel):
    """Contains the NCGI (NR Cell Global Identity), as described in 3GPP 23.003"""
    plmnId: PlmnId
    nrCellId: constr(regex=r'^[A-Fa-f0-9]{9}$')
    nid: Optional[constr(regex=r'^[A-Fa-f0-9]{11}$')]


#TS 29.571
class GNbId(BaseModel):
    """Provides the G-NB identifier."""
    bitLength: int = Field(None, description="", ge=22, le=32)
    gNBValue: constr(regex=r'^[A-Fa-f0-9]{6,8}$')

#TS 29.571
class GlobalRanNodeId(BaseModel):
    """One of the six attributes n3IwfId, gNbIdm, ngeNbId, wagfId, tngfId, eNbId shall be present."""
    plmnId: PlmnId
    n3IwfId: Optional[constr(regex=r'^[A-Fa-f0-9]+$')]
    gNbId: Optional[GNbId]
    ngeNbId: Optional[constr(regex=r'^(MacroNGeNB-[A-Fa-f0-9]{5}|LMacroNGeNB-[A-Fa-f0-9]{6}|SMacroNGeNB-[A-Fa-f0-9]{5})$')]
    wagfId: Optional[constr(regex=r'^[A-Fa-f0-9]+$')]
    tngfId: Optional[constr(regex=r'^[A-Fa-f0-9]+$')]
    nid: constr(regex=r'^[A-Fa-f0-9]{11}$')
    eNbId: Optional[constr(regex=r'^(MacroeNB-[A-Fa-f0-9]{5}|LMacroeNB-[A-Fa-f0-9]{6}|SMacroeNB-[A-Fa-f0-9]{5}|HomeeNB-[A-Fa-f0-9]{7})$')]

#TS 29.571
class Tai(BaseModel):
    """Contains the tracking area identity as described in 3GPP 23.003"""
    plmnId: PlmnId
    tac: constr(regex=r'(^[A-Fa-f0-9]{4}$)|(^[A-Fa-f0-9]{6}$)')
    nid: Optional[constr(regex=r'^[A-Fa-f0-9]{11}$')]

#TS 29.571
class EutraLocation(BaseModel):
    """Contains the E-UTRA user location.""" 
    tai: Tai
    ignoreTai: bool = Field(False)
    ecgi: Ecgi
    ignoreEcgi: bool = Field(False)
    ageOfLocationInformation: int = Field(None, description="", ge=0, le=32767)
    ueLocationTimestamp: datetime
    geographicalInformation: constr(regex=r'^[0-9A-F]{16}$')
    geodeticInformation: constr(regex=r'^[0-9A-F]{20}$')
    globalNgenbId: GlobalRanNodeId
    globalENbId: GlobalRanNodeId

#TS 29.571
class NrLocation(BaseModel):
    """Contains the NR user location.""" 
    tai: Tai
    ignoreTai: bool = Field(False)
    ncgi: Ncgi
    ignoreNcgi: bool = Field(False)
    ageOfLocationInformation: int = Field(None, description="", ge=0, le=32767)
    ueLocationTimestamp: datetime
    geographicalInformation: constr(regex=r'^[0-9A-F]{16}$')
    geodeticInformation: constr(regex=r'^[0-9A-F]{20}$')
    globalGnbId: GlobalRanNodeId

#TS 29.571
#TODO: doing
class N3gaLocation(BaseModel):
    """Contains the Non-3GPP access user location.""" 
    n3gppTai: Tai
    n3IwfId: constr(regex=r'^[A-Fa-f0-9]+$')
    


#TS 29.571
class UserLocation(BaseModel):
    """At least one of eutraLocation, nrLocation and n3gaLocation shall be present. Several 
 of them may be present."""
    eutraLocation: EutraLocation
    nrLocation: NrLocation
    n3gaLocation: N3gaLocation
    utraLocation: UtraLocation
    geraLocation: GeraLocation


#TS 29.122
class DayOfWeek(BaseModel):
    day: int = Field(None, description="", ge=1, le=7)