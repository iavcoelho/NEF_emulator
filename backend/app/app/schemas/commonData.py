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
#Gpsi
#Uri
#ApplicationId - str --- String providing an application identifier. 
#BitRate - constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')
#Uinteger - int -> ge = 0
#Float - float
#SamplingRatio - int -> ge = 1, le = 100 --- expressed in percent
#PacketDelBudget - int -> ge = 1 --- expressed in milliseconds.
#PacketLossRate - int -> ge = 0, le = 1000 --- expressed in tenth of percent

#TODO:
#29.122
#WebsockNotifConfig
#LocationArea
#LocationArea5G
#ConfigResult
#TimeWindo
#FlowInfo

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

