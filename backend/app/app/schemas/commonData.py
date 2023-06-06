from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress, AnyHttpUrl, constr
from enum import Enum


#Defined with other classes, without making a new class type
#Link - AnyHttpUrl
#DateTime - datetime
#Dnn - Optional[str] = Field("province1.mnc01.mcc202.gprs", description="String identifying the Data Network Name (i.e., Access Point Name in 4G). For more information check clause 9A of 3GPP TS 23.003")
#ExternalId - str -> example: 123456789@domain.com
#Msisdn - str -> example: 918369110173
#ExternalGroupId - str -> example: Group1@domain.com
#IpAddr - IPvAnyAddress
#MacAddr48 - constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$')
#DurationSec - int = Field(None, description="", ge=0)
#DayOfWeek ???
#TimeOfDay ???
#DurationSecRm ???
#DurationSecRo ???

#TODO:
#29.571
#SupportedFeatures - constr(regex=r'^[A-Fa-f0-9]*$')
#Dnai - str --- DNAI (Data network access identifier), see clause 5.6.7 of 3GPP TS 23.501.
#TypeAllocationCode
#Gpsi ---  constr(regex=r'^(msisdn-[0-9]{5,15}|extid-.+@.+|.+)$')
#Uri - str
#ApplicationId - str = Field(None, description="String providing an application identifier.")
#BitRate - constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')
#Uinteger - int = Field(None, description="", ge=0)
#Float - float
#SamplingRatio - int = Field(None, description="Expressed in percent.", ge=1, le=100)
#PacketDelBudget - int = Field(None, description="Expressed in milliseconds.", ge=1)
#PacketLossRate - int = Field(None, description="Expressed in tenth of percent.", ge=0, le=1000)
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
#Supi - constr(regex=r'^(imsi-[0-9]{5,15}|nai-.+|gci-.+|gli-.+|.+)$')
#Bytes - constr(regex=r'^@(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')
# HfcNodeId ---> str = Field(None, description="REpresents the HFC Node Identifer received over NGAP.", max_digits=6)
# Gli - Bytes
# Gci: str = Field(None, description="Global Cable Identifier uniquely identifying the connection between the 5G-CRG or FN-CRG to the 5GS. See clause 28.15.4 of 3GPP TS 23.003. This shall be encoded as a string per clause 28.15.4 of 3GPP TS 23.003, and compliant with the syntax specified in clause 2.2 of IETF RFC 7542 for the username part of a NAI. The GCI value is specified in CableLabs WR-TR-5WWC-ARCH.")
#ArfcnValueNR - int = Field(None, description="", ge=0, le=3279165)
#RatType
#5Qi - int = Field(None, description="", ge=0, le=255)
#PacketErrRate - constr(regex=r'^([0-9]E-[0-9])$')

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

#TS 29.122
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
class CellGlobalId(BaseModel):
    """Contains a Cell Global Identification as defined in 3GPP TS 23.003, clause 4.3.1.""" 
    plmnId: PlmnId
    lac: constr(regex=r'^[A-Fa-f0-9]{4}$')
    cellId: constr(regex=r'^[A-Fa-f0-9]{4}$')

#TS 29.571
class ServiceAreaId(BaseModel):
    """Contains a Service Area Identifier as defined in 3GPP TS 23.003, clause 12.5.""" 
    plmnId: PlmnId
    lac: constr(regex=r'^[A-Fa-f0-9]{4}$') = Field(None, description="Location Area Code.")
    sac: constr(regex=r'^[A-Fa-f0-9]{4}$') = Field(None, description="Service Area Code.")


#TS 29.571
class LocationAreaId(BaseModel):
    """Contains a Location area identification as defined in 3GPP TS 23.003, clause 4.1.""" 
    plmnId: PlmnId
    lac: constr(regex=r'^[A-Fa-f0-9]{4}$') = Field(None, description="Location Area Code.")

#TS 29.571
class RoutingAreaId(BaseModel):
    """Contains a Routing Area Identification as defined in 3GPP TS 23.003, clause 4.2.""" 
    plmnId: PlmnId
    lac: constr(regex=r'^[A-Fa-f0-9]{4}$') = Field(None, description="Location Area Code.")
    rac: constr(regex=r'^[A-Fa-f0-9]{2}$') = Field(None, description="Routing Area Code.")

#TS 29.571
class UtraLocation(BaseModel):
    """Exactly one of cgi, sai or lai shall be present.""" 
    cgi: CellGlobalId
    sai: ServiceAreaId
    lai: LocationAreaId
    rai: RoutingAreaId
    ageOfLocationInformation: int = Field(None, description="", ge=0, le=32767)
    ueLocationTimestamp: datetime
    geographicalInformation: constr(regex=r'^[0-9A-F]{16}$')
    geodeticInformation: constr(regex=r'^[0-9A-F]{20}$')

#TS 29.571
class TransportProtocol(str, Enum):
    udp = "UDP" 
    tcp = "TCP" 


#TS 29.571
class LineType(str, Enum):
    dsl = "DSL" 
    pon = "PON" 

#TS 29.571
class TnapId(BaseModel):
    """Contain the TNAP Identifier see clause5.6.2 of 3GPP TS 23.501.""" 
    ssId: str = Field(None, description="This IE shall be present if the UE is accessing the 5GC via a trusted WLAN access network.When present, it shall contain the SSID of the access point to which the UE is attached, that is received over NGAP, see IEEE Std 802.11-2012. ")
    bssId: Optional[str] = Field(None, description="When present, it shall contain the BSSID of the access point to which the UE is attached, that is received over NGAP, see IEEE Std 802.11-2012.")
    civicAddress: constr(regex=r'^@(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')

#TS 29.571
class TwapId(BaseModel):
    """Contain the TWAP Identifier as defined in clause 4.2.8.5.3 of 3GPP TS 23.501 or the WLAN location information as defined in clause 4.5.7.2.8 of 3GPP TS 23.402.""" 
    ssId: str = Field(None, description="This IE shall contain the SSID of the access point to which the UE is attached, that is received over NGAP, see IEEE Std 802.11-2012. ")
    bssId: Optional[str] = Field(None, description="When present, it shall contain the BSSID of the access point to which the UE is attached, for trusted WLAN access, see IEEE Std 802.11-2012.")
    civicAddress: constr(regex=r'^@(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')

#TS 29.571
class NThreegaLocation(BaseModel):
    """Contains the Non-3GPP access user location.""" 
    n3gppTai: Tai
    n3IwfId: constr(regex=r'^[A-Fa-f0-9]+$')
    ueIpv4Addr: AnyHttpUrl = Field(None, description="String identifying an Ipv4 address")  
    ueIpv6Addr: AnyHttpUrl = Field(None, description="String identifying an Ipv6 address")  
    portNumber: int = Field(None, description="", ge=0)
    protocol: TransportProtocol
    tnapId: TnapId
    twapId: TwapId
    hfcNodeId: str = Field(None, description="REpresents the HFC Node Identifer received over NGAP.", max_length=6)
    gli: constr(regex=r'^@(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$')
    w5gbanLineType: LineType
    gci: str = Field(None, description="Global Cable Identifier uniquely identifying the connection between the 5G-CRG or FN-CRG to the 5GS. See clause 28.15.4 of 3GPP TS 23.003. This shall be encoded as a string per clause 28.15.4 of 3GPP TS 23.003, and compliant with the syntax specified in clause 2.2 of IETF RFC 7542 for the username part of a NAI. The GCI value is specified in CableLabs WR-TR-5WWC-ARCH.")

#TS 29.571
class GeraLocation(BaseModel):
    """Contains the Non-3GPP access user location.""" 
    locationNumber: str = Field(None, description="Location number within the PLMN. See 3GPP TS 23.003, clause 4.5. ")
    cgi: CellGlobalId
    rai: RoutingAreaId
    sai: ServiceAreaId
    lai: LocationAreaId
    vlrNumber: str = Field(None, description="VLR number. See 3GPP TS 23.003 clause 5.1.")
    mscNumber: str = Field(None, description="MSC number. See 3GPP TS 23.003 clause 5.1. ")
    ageOfLocationInformation: int = Field(None, description="", ge=0, le=32767)
    ueLocationTimestamp: datetime
    geographicalInformation: constr(regex=r'^[0-9A-F]{16}$')
    geodeticInformation: constr(regex=r'^[0-9A-F]{20}$')

#TS 29.571
class UserLocation(BaseModel):
    """At least one of eutraLocation, nrLocation and n3gaLocation shall be present. Several 
 of them may be present."""
    eutraLocation: EutraLocation
    nrLocation: NrLocation
    # n3gaLocation: NThreegaLocation
    utraLocation: UtraLocation
    geraLocation: GeraLocation

#TS 29.122
class DayOfWeek(BaseModel):
    day: int = Field(None, description="", ge=1, le=7)


#TS 29.571
class RatType(str, Enum):
    """Indicates the radio access used."""
    nr = "NR" 
    eutra = "EUTRA" 
    wlan = "WLAN" 
    virtual = "VIRTUAL" 
    nbiot = "NBIOT" 
    wireline = "WIRELINE" 
    wirelineCable = "WIRELINE_CABLE" 
    wirelineBbf = "WIRELINE_BBF" 
    lteM = "LTE-M" 
    nrU = "NR_U" 
    eutraU = "EUTRA_U" 
    trustedN3ga = "TRUSTED_N3GA" 
    trustedWlan = "TRUSTED_WLAN" 
    utra = "UTRA" 
    gera = "GERA" 
    nrLeo = "NR_LEO" 
    nrMeo = "NR_MEO" 
    nrGeo = "NR_GEO" 
    nrOtherSat = "NR_OTHER_SAT" 
    nrRedcap= "NR_REDCAP" 

#TS 29.571
class QosResourceType(str, Enum):
    nonGbr = "NON_GBR" 
    nonCriticalGbr = "NON_CRITICAL_GBR" 
    criticalGbr = "CRITICAL_GBR" 

#TS 29.571
class AnalyticsSubset(str, Enum):
    numOfUeReg = "NUM_OF_UE_REG" 
    numOfPduSessEstbl = "NUM_OF_PDU_SESS_ESTBL" 
    resUsage = "RES_USAGE" 
    numOfExceedResUsageLoadLevelThr = "NUM_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR" 
    periodOfExceedResUsageLoadLevelThr = "PERIOD_OF_EXCEED_RES_USAGE_LOAD_LEVEL_THR" 
    exceedLoadLevelThrInd = "EXCEED_LOAD_LEVEL_THR_IND" 
    listOfTopAppUl = "LIST_OF_TOP_APP_UL" 
    listOfTopAppDl = "LIST_OF_TOP_APP_DL" 
    nfStatus = "NF_STATUS" 
    nfResourceUsage = "NF_RESOURCE_USAGE" 
    nfLoad = "NF_LOAD" 
    nfPeakLoad = "NF_PEAK_LOAD" 
    nfLoadAvgInAoi = "NF_LOAD_AVG_IN_AOI" 
    disperAmount = "DISPER_AMOUNT" 
    disperClass = "DISPER_CLASS" 
    ranking = "RANKING" 
    percentileRanking = "PERCENTILE_RANKING" 
    rssi = "RSSI" 
    rtt = "RTT" 
    trafficInfo = "TRAFFIC_INFO" 
    numberOfUes = "NUMBER_OF_UES" 
    appListForUeComm = "APP_LIST_FOR_UE_COMM" 
    n4SessInactTimerForEuComm = "N4_SESS_INACT_TIMER_FOR_UE_COMM" 
    avgTrafficRate = "AVG_TRAFFIC_RATE"
    maxTrafficRate = "MAX_TRAFFIC_RATE" 
    avgPacketDelay = "AVG_PACKET_DELAY" 
    maxPacketDelay = "MAX_PACKET_DELAY" 
    avgPacketLossRate = "AVG_PACKET_LOSS_RATE" 
    ueLocation = "UE_LOCATION" 
    listOfHighExpUe = "LIST_OF_HIGH_EXP_UE" 
    listOfMediumExpUe = "LIST_OF_MEDIUM_EXP_UE" 
    lsitOfLowExpUe = "LIST_OF_LOW_EXP_UE" 
    avgUlPktDropRate = "AVG_UL_PKT_DROP_RATE" 
    varUlPktDropRate = "VAR_UL_PKT_DROP_RATE" 
    avgDlPktDropRate = "AVG_DL_PKT_DROP_RATE" 
    varDlPktDropRate = "VAR_DL_PKT_DROP_RATE" 
    avgUlPktDelay = "AVG_UL_PKT_DELAY" 
    varUlPktDelay = "VAR_UL_PKT_DELAY" 
    avgDlPktDelay = "AVG_DL_PKT_DELAY" 
    varDlPktDelay = "VAR_DL_PKT_DELAY"

#TS 29.571
class PartitioningCriteria(str, Enum):
    tac = "TAC" 
    subPlmn = "SUBPLMN" 
    geoArea = "GEOAREA"
    snssai = "SNSSAI" 
    dnn = "DNN"

#TS 29.571
class NotificationFlag(str, Enum):
    activate = "ACTIVATE" 
    deactivate = "DEACTIVATE" 
    retrieval = "RETRIEVAL"

#TS 29.122
class WebsockNotifConfig(BaseModel):
    """Represents the configuration information for the delivery of notifications over Websockets."""
    websocketUri: AnyHttpUrl
    requestWebsocketUri: bool = Field(None, description=" Set by the SCS/AS to indicate that the Websocket delivery is requested.")

#TS 29.122
#TODO: locationArea5g
# class LocationArea5G(BaseModel):
#     """Represents a user location area when the UE is attached to 5G. """
#     geographicAreas: List[GeographicArea] = Field(None, description="Identifies a list of geographic area of the user where the UE is located.", min_items=0)
#     civicAddresses: List[CivicAddress] = Field(None, description="Identifies a list of civic addresses of the user where the UE is located.", min_items=0)
#     nwAreaInfo: NetworkAreaInfo