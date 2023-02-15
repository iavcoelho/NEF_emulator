from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress, AnyHttpUrl, constr
from enum import Enum
from .commonData import Snssai, TimeWindow, FlowInfo, Ecgi, Ncgi, GlobalRanNodeId, Tai
from .cpParameterProvisioning import ScheduledCommunicationTime

############### TS 29.554 Types ###############

class NetworkAreaInfo(BaseModel):
    """Describes a network area information in which the NF service consumer requests the number of UEs. """
    ecgis: List[Ecgi] = Field(None, description="Contains a list of E-UTRA cell identities.", min_items=1)
    ncgis: List[Ncgi] = Field(None, description="Contains a list of NR cell identities.", min_items=1)
    gRanNodeIds: List[GlobalRanNodeId] = Field(None, description="Contains a list of NG RAN nodes.", min_items=1)
    tais: List[Tai] = Field(None, description="Contains a list of tracking area identities.", min_items=1)
    

###############################################

############### TS 29.512 Types ###############

class FlowDirection(str, Enum):
    downlink = "DOWNLINK" 
    uplink = "UPLINK" 
    bidirectional = "BIDIRECTIONAL" 
    unspecified = "UNSPECIFIED"

###############################################

############### TS 29.514 Types ###############

class EthFlowDescription(BaseModel):
    """Identifies an Ethernet flow."""
    destMacAddr: constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$')
    ethType: str
    fDesc: str = Field(None, description="Defines a packet filter of an IP flow.")
    fDir: FlowDirection
    sourceMacAddr: constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$')
    vlanTags: List[str] = Field(None, description="", min_items=1, max_items=2)
    srcMacAddrEnd: constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$')
    destMacAddrEnd: constr(regex=r'^([0-9a-fA-F]{2})((-[0-9a-fA-F]{2}){5})$')

###############################################


############### TS 29.520 Types ###############

class NetworkPerfType(str, Enum):
    gnbActiveRatio = "GNB_ACTIVE_RATIO" 
    gnbComputingUsage = "GNB_COMPUTING_USAGE" 
    gnbMemoryUsage = "GNB_MEMORY_USAGE" 
    gnbDiskUsage = "GNB_DISK_USAGE" 
    numOfUE = "NUM_OF_UE" 
    sessSuccRatio = "SESS_SUCC_RATIO" 
    hoSuccRatio = "HO_SUCC_RATIO" 

class ExceptionId(str, Enum):
    unexpectedUELocation = "UNEXPECTED_UE_LOCATION" 
    unexpectedLongLiveFlow = "UNEXPECTED_LONG_LIVE_FLOW" 
    unexpectedLargeRateFlow = "UNEXPECTED_LARGE_RATE_FLOW" 
    unexpectedWakeup= "UNEXPECTED_WAKEUP" 
    suspecionOfDdosAttack = "SUSPICION_OF_DDOS_ATTACK" 
    wrongDestinationAddress = "WRONG_DESTINATION_ADDRESS" 
    tooFrequentServiceAccess = "TOO_FREQUENT_SERVICE_ACCESS" 
    unexpectedRatioLinkFailures = "UNEXPECTED_RADIO_LINK_FAILURES" 
    pingPongAcrossCells = "PING_PONG_ACROSS_CELLS"

class ExceptionTrend(str, Enum):
    up = "UP" 
    down = "DOWN" 
    unknow = "UNKNOW" 
    stable = "STABLE"

class DispersionClass(str, Enum):
    fixed = "FIXED" 
    camper = "CAMPER" 
    traveller = "TRAVELLER" 
    topHeavy = "TOP_HEAVY"

class CongestionType(str, Enum):
    userPlane = "USER_PLANE" 
    controlPlane = "CONTROL_PLANE" 
    userAndControlPlane = "USER_AND_CONTROL_PLANE" 

class TimeUnit(str, Enum):
    minute = "MINUTE" 
    hour = "HOUR" 
    day = "DAY" 

class RetainabilityThreshold(BaseModel):
    """Represents a QoS flow retainability threshold."""
    relFlowNum: int = Field(None, description="", ge=0)
    relTimeUnit: TimeUnit
    relFlowRatio:  int = Field(None, description="Expressed in percent", ge=1, le=100)

class ThresholdLevel(BaseModel):
    """Represents a threshold level."""
    congLevel: int
    nfLoadLevel: int
    nfCpuUsage: int
    nfMemoryUsage: int
    nfStorageUsage: int
    avgTrafficRate: constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')
    maxTrafficRate: constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')
    avgPacketDelay: int = Field(None, description="Expressed in milliseconds.", ge=1)
    maxPacketDelay: int = Field(None, description="Expressed in milliseconds.", ge=1)
    avgPacketLossRate: int = Field(None, description="Expressed in tenth of percent", ge=0, le=1000)
    svcExpLevel: float

class TopApplication(BaseModel):
    """Top application that contributes the most to the traffic. """
    appId: str = Field(None, description="String providing an application identifier.")
    ipTrafficFilter: FlowInfo
    ratio: constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')

class Exception(BaseModel):
    """Represents the Exception information."""
    excepId: ExceptionId
    excepLevel: int
    excepTrend: ExceptionTrend

class IpEthFlowDescription(BaseModel):
    """Contains the description of an Uplink and/or Downlink Ethernet flow."""
    ipTrafficFilter: str = Field(None, description="Defines a packet filter of an IP flow.")
    ethTrafficFilter: EthFlowDescription

class AddressList(BaseModel):
    """Represents a list of IPv4 and/or IPv6 addresses."""
    ipv4Addrs: List[IPvAnyAddress] = Field(None, description="String identifying an Ipv4 address", min_items=1)
    ipv6Addrs: List[IPvAnyAddress] = Field(None, description="String identifying an Ipv6 address", min_items=1)

class CircumstanceDescription(BaseModel):
    """Contains the description of a circumstance."""
    freq: float
    tm: datetime
    locArea: NetworkAreaInfo
    vol: int = Field(None, description=" Unsigned integer identifying a volume in units of bytes.", ge=0)

class AdditionalMeasurement(BaseModel):
    """Represents additional measurement information."""
    #TODO: 29.554 NetworkAreaInfo
    unexpLoc: NetworkAreaInfo
    unexpFlowTeps: List[IpEthFlowDescription] = Field(None, description="", min_items=1)
    unexpWakes: List[datetime] = Field(None, description="", min_items=1)
    ddosAttack: AddressList
    wrgDest: AddressList
    circums: List[CircumstanceDescription] = Field(None, description="", min_items=1)

class TrafficCharacterization(BaseModel):
    """Identifies the detailed traffic characterization."""
    dnn: str = Field("province1.mnc01.mcc202.gprs", description="String identifying the Data Network Name (i.e., Access Point Name in 4G). For more information check clause 9A of 3GPP TS 23.003")
    snssai: Snssai
    appId: str = Field("", description="String providing an application identifier.")
    fDescs: List[IpEthFlowDescription] = Field(None, description="", min_items=1, max_items=2)
    ulVol: int = Field(None, description=" Unsigned integer identifying a volume in units of bytes.", ge=0)
    ulVolVariance: float
    dlVol: int = Field(None, description=" Unsigned integer identifying a volume in units of bytes.", ge=0)
    dlVolVariance: float

class AppListForUeComm(BaseModel):
    """Represents the analytics of the application list used by UE. """
    appId: str = Field("", description="String providing an application identifier.")
    startTime: datetime
    appDur: int = Field(None, description="", ge=0)
    occurRatio: int = Field(None, description="Expressed in percent", ge=1, le=100)
    spatialValidity: NetworkAreaInfo

class SessInactTimerForUeComm(BaseModel):
    """Represents the N4 Session inactivity timer."""
    n4SessId: int = Field(None, description="", ge=0, le=255)
    sessInactiveTimer: int = Field(None, description="", ge=0)

class UeCommunication(BaseModel):
    """Represents UE communication information."""
    commDur: int = Field(None, description="", ge=0)
    commDurVariance: float
    perioTime: int = Field(None, description="", ge=0)
    perioTimeVariance: float
    ts: int = Field(None, description="", ge=0)
    tsVariance: float
    recurringTime: ScheduledCommunicationTime
    trafChar: TrafficCharacterization
    ratio: int = Field(None, description="", ge=1, le=100)
    perioCommInd: bool
    confidence: int = Field(None, description="", ge=0)
    anaOfAppList: AppListForUeComm
    sessInactTimer: SessInactTimerForUeComm

class ApplicationVolume(BaseModel):
    """ApplicationVolume"""
    appId: str = Field(None, description="String providing an application identifier.")
    appVolume: int = Field(None, description="", ge=0)

class DispersionCollection(BaseModel):
    """Dispersion collection per UE location or per slice."""
    ueLoc: UserLocation
    snssai: Snssai
    supis: List[Supi] = Field(None, description="", min_items=1)
    gpsis: List[constr(regex=r'^(msisdn-[0-9]{5,15}|extid-.+@.+|.+)$')] = Field(None, description="", min_items=1)
    appVolumes: List[ApplicationVolume] = Field(None, description="", min_items=1)
    disperAmount: int = Field(None, description="", ge=0)
    disperClass: DispersionClass
    usageRank: int = Field(None, description="", ge=1, le=3)
    percentileRank: int = Field(None, description="", ge=1, le=100)
    ueRatio: int = Field(None, description="", ge=1, le=100)
    confidence: int = Field(None, description="", ge=0)

class DispersionInfo(BaseModel):
    """Represents the Dispersion information. When subscribed event is "DISPERSION", the 
 "disperInfos" attribute shall be included."""
    tsStart: datetime
    tsDuration: int = Field(None, description="", ge=0)
    disperCollects: List[DispersionCollection] = Field(None, description="", min_items=1)
    disperType = DispersionType

###############################################

class AnalyticsFailureCode(str, Enum):
    unavailableData = "UNAVAILABLE_DATA" 
    bothStatPredNotAllowed = "BOTH_STAT_PRED_NOT_ALLOWED" 
    unsatifiedRequestAnalyticsTime = "UNSATISFIED_REQUESTED_ANALYTICS_TIME" 
    other = "OTHER" 

class AnalyticsEvent(str, Enum):
    ueMobility = "UE_MOBILITY" 
    ueComm = "UE_COMM" 
    abnormalBehavior = "ABNORMAL_BEHAVIOR" 
    congestion = "CONGESTION" 
    networkPerformance = "NETWORK_PERFORMANCE" 
    qosSustainability = "QOS_SUSTAINABILITY" 
    dispersion = "DISPERSION" 
    dnPerformance = "DN_PERFORMANCE" 
    serviceExperience = "SERVICE_EXPERIENCE"

class UeLocationInfo(BaseModel):
    """Represents a UE location information."""
    # loc: LocationArea5G
    ratio: int = Field(None, description="Expressed in percent", ge=1, le=100)
    confidence: int = Field(None, description="", ge=0)

class UeMobilityExposure(BaseModel):
    """Represents a UE mobility information."""
    ts: datetime
    recurringTime: ScheduledCommunicationTime
    duration: int = Field(None, description="", ge = 0)
    durationVariance: float
    locInfo: List[UeLocationInfo] = Field(None, description="", min_items=1)

class AnalyticsFailureEventInfo(BaseModel):
    """Represents an event for which the subscription request was not successful 
and including the associated failure reason. """
    event: AnalyticsEvent
    failureCode: AnalyticsFailureCode

class QosSustainabilityExposure(BaseModel):
    """Represents a QoS sustainability information."""
    #TODO: LocationArea5G
    # locArea: LocationArea5G
    startTs: datetime
    endTs: datetime
    qosFlowRetThd: RetainabilityThreshold
    ranUeThrouThd: constr(regex=r'^\d+(\.\d+)? (bps|Kbps|Mbps|Gbps|Tbps)$')
    snssai: Snssai
    confidence: int = Field(None, description="", ge=0)

class CongestionAnalytics(BaseModel):
    """Represents data congestion analytics for transfer over the user plane, 
 control plane or both."""
    cngType: CongestionType
    tmWdw: TimeWindow
    nsi: ThresholdLevel
    confidence: int = Field(None, description="", ge=0)
    topAppListUl: List[TopApplication] = Field(None, description="", min_items=1)
    topAppListDl: List[TopApplication] = Field(None, description="", min_items=1)

class CongestInfo(BaseModel):
    """Represents a UE's user data congestion information."""
    # locArea: LocationArea5G
    cngAnas: List[CongestionAnalytics] = Field(None, description="", min_items=1)

class AbnormalExposure(BaseModel):
    """Represents a user's abnormal behavior information."""
    #TODO: test this list
    gpsis: List[constr(regex=r'^(msisdn-[0-9]{5,15}|extid-.+@.+|.+)$')] = Field(None, description="", min_items=1)
    appId: str = Field(None, description="String providing an application identifier.")
    dnn: Optional[str] = Field("province1.mnc01.mcc202.gprs", description="String identifying the Data Network Name (i.e., Access Point Name in 4G). For more information check clause 9A of 3GPP TS 23.003")
    snssai: Snssai
    excep: List[Exception]
    ratio: int = Field(None, description="Expressed in percent", ge=1, le=100)
    confidence: int = Field(None, description="", ge=0)
    addtMeasInfo: AdditionalMeasurement

class NetworkPerfExposure(BaseModel):
    """Represents network performance information."""
    # locArea: LocationArea5G
    nwPerfType: NetworkPerfType
    relativeRatio: int = Field(None, description="Expressed in percent", ge=1, le=100)
    absoluteNum: int = Field(None, description="", ge=0)
    confidence: int = Field(None, description="", ge=0)

class AnalyticsData(BaseModel):
    """Represents analytics data."""
    start: datetime
    expiry: datetime
    timeStampGen: datetime
    ueMobilityInfos: List[UeMobilityExposure] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 UeCommunication
    ueCommInfos: List[UeCommunication] = Field(None, description="", min_items=1)
    nwPerfInfos: List[NetworkPerfExposure] = Field(None, description="", min_items=1)
    abnormalInfos: List[AbnormalExposure] = Field(None, description="", min_items=1)
    congestInfos: List[CongestInfo] = Field(None, description="", min_items=1)
    qosSustainInfos: List[QosSustainabilityExposure] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DispersionInfo
    disperInfos: List[DispersionInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DnPerfInfo
    dnPerfInfos: List[DnPerfInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 ServiceExperienceInfo
    svcExps: List[ServiceExperienceInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DispersionRequirement
    disperReqs: List[DispersionRequirement] = Field(None, description="", min_items=1)
    suppFeat: SupportedFeatures

class AnalyticsEventFilter(BaseModel):
    """ Represents analytics event filter information."""
    # locArea: LocationArea5G
    dnn: Optional[str] = Field("province1.mnc01.mcc202.gprs", description="String identifying the Data Network Name (i.e., Access Point Name in 4G). For more information check clause 9A of 3GPP TS 23.003")
    dnais: List[Dnai] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 NetworkPerfType
    nwPerfTypes: List[NetworkPerfType] = Field(None, description="", min_items=1)
    appIds: List[ApplicationId] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 ExceptionId
    appIds: List[ExceptionId] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 ExpectedAnalyticsType
    exptAnaType: ExpectedAnalyticsType
    #TODO: ts 29.503 ExpectedUeBehaviourData
    exptUeBehav: ExpectedUeBehaviourData
    snssai: Snssai
    #TODO: ts 29.520 NsiIdInfo
    nsiIdInfos: List[NsiIdInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 QosRequirement
    qosReq: QosRequirement
    #TODO: ts 29.520 AnalyticsSubset
    listOfAnaSubsets: List[AnalyticsSubset] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DnPerformanceReq
    dnPerfReqs: List[DnPerformanceReq] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 BwRequirement
    bwRequs: List[BwRequirement] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 RatFreqInformation
    ratFreqs: List[RatFreqInformation] = Field(None, description="", min_items=1)    
    #TODO: ts 29.520 AddrFqdn
    appServerAddrs: List[AddrFqdn] = Field(None, description="", min_items=1)
    maxNumOfTopAppUl: int = Field(None, description="", ge=0)
    maxNumOfTopAppDl: int = Field(None, description="", ge=0)
    visitedLocAreas: List[LocationArea5G] = Field(None, description="", min_items=1)

class AnalyticsRequest(BaseModel):
    """Represents the parameters to request to retrieve analytics information."""
    analyEvent: AnalyticsEvent
    analyEventFilter: AnalyticsEventFilter
    #TODO: ts 29.520 EventReportingRequirement
    analyRep: EventReportingRequirement
    tgtUe: TargetUeId
    suppFeat: SupportedFeatures

class UeLocationInfo(BaseModel):
    """Represents a UE location information."""
    loc: LocationArea5G
    ratio: int = Field(None, description="Expressed in percent", ge=1, le=100)
    confidence: int = Field(None, description="", ge=0)

class TargetUeId(BaseModel):
    """ Represents a UE mobility information."""
    ts: datetime
    #TODO: ts 29.122 ScheduledCommunicationTime
    recurringTime: ScheduledCommunicationTime
    duration: int = Field(None, description="", ge=0)
    durationVariance: Float
    locInfo: List[UeLocationInfo] = Field(None, description="", min_items=1)

class TargetUeId(BaseModel):
    """Represents the target UE(s) information."""
    anyUeInd: bool
    gpsi: gpsi
    exterGroupId: str = Field("Group1@domain.com", description="")

class AnalyticsEventFilterSubsc(BaseModel):
    """Represents an analytics event filter."""
    #TODO: ts 29.520 NetworkPerfRequirement
    nwPerfReqs: List[NetworkPerfRequirement] = Field(None, description="", min_items=1)
    locArea: LocationArea5G
    appIds: List[ApplicationId] = Field(None, description="", min_items=1)
    dnn: Optional[str] = Field("province1.mnc01.mcc202.gprs", description="String identifying the Data Network Name (i.e., Access Point Name in 4G). For more information check clause 9A of 3GPP TS 23.003")
    dnais: List[Dnai] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 Exception
    # excepRequs: List[Exception] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 ExpectedAnalyticsType
    exptAnaType: ExpectedAnalyticsType
    #TODO: ts 29.503 ExpectedUeBehaviourData
    exptUeBehav: ExpectedUeBehaviourData
    #TODO: ts 29.520 MatchingDirection
    matchingDir: MatchingDirection
    #TODO: ts 29.520 ThresholdLevel
    reptThlds: List[ThresholdLevel] = Field(None, description="", min_items=1)
    snssai: Snssai
    #TODO: ts 29.520 NsiIdInfo
    nsiIdInfos: List[NsiIdInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 QosRequirement
    qosReq: QosRequirement
    #TODO: ts 29.520 RetainabilityThreshold
    qosFlowRetThds: List[RetainabilityThreshold] = Field(None, description="", min_items=1)
    ranUeThrouThds: List[BitRate] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DispersionRequirement
    disperReqs: List[DispersionRequirement] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 AnalyticsSubset
    listOfAnaSubsets: List[AnalyticsSubset] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DnPerformanceReq
    dnPerfReqs: List[DnPerformanceReq] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 BwRequirement
    bwRequs: List[BwRequirement] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 RatFreqInformation
    ratFreqs: List[RatFreqInformation] = Field(None, description="", min_items=1)
    #TODO: ts 29.517 AddrFqdn
    appServerAddrs: List[AddrFqdn] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 AddrFqdn
    extraReportReq: List[EventReportingRequirement] = Field(None, description="", min_items=1)
    maxNumOfTopAppUl: int = Field(None, description="", ge=0)
    maxNumOfTopAppDl: int = Field(None, description="", ge=0)
    visitedLocAreas: List[LocationArea5G] = Field(None, description="", min_items=1)

class AnalyticsEventNotif(BaseModel):
    """Represents a subscribed analytics event."""
    analyEvent: AnalyticsEvent
    analyEventFilter: AnalyticsEventFilterSubsc
    tgtUe: TargetUeId

class AnalyticsEventNotif(BaseModel):
    """Represents an analytics event to be reported."""
    analyEvent: AnalyticsEvent
    expiry: datetime
    timeStamp: datetime
    #TODO: ts 29.520 NwdafFailureCode
    failNotifyCode: NwdafFailureCode
    rvWaitTime: int = Field(None, description="", ge=0)
    ueMobilityInfos: List[UeMobilityExposure] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 UeCommunication
    ueCommInfos: List[UeCommunication] = Field(None, description="", min_items=1)
    abnormalInfos: List[AbnormalExposure] = Field(None, description="", min_items=1)
    congestInfos: List[CongestInfo] = Field(None, description="", min_items=1)
    nwPerfInfos: List[NetworkPerfExposure] = Field(None, description="", min_items=1)
    qosSustainInfos: List[QosSustainabilityExposure] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DispersionInfo
    disperInfos: List[DispersionInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 DnPerfInfo
    dnPerfInfos: List[DnPerfInfo] = Field(None, description="", min_items=1)
    #TODO: ts 29.520 ServiceExperienceInfo
    svcExps: List[ServiceExperienceInfo] = Field(None, description="", min_items=1)
    start: datetime
    timeStampGen: datetime

class AnalyticsEventNotification(BaseModel):
    """Represents an analytics event(s) notification."""
    notifId: str
    analyEventNotifs: List[AnalyticsEventNotif] = Field(None, description="", min_items=1)

class AnalyticsExposureSubscCreate(BaseModel):
    """Represents an analytics exposure subscription."""
    analyEventsSubs: List[AnalyticsEventSubsc] = Field(None, description="", min_items=1)
    analyRepInfo:ReportingInformation
    notifUri: Uri
    notifId: str
    eventNotifis: List[AnalyticsEventNotif] = Field(None, description="", min_items=1)
    failEventReports: List[AnalyticsFailureEventInfo] = Field(None, description="", min_items=1)
    suppFeat: SupportedFeatures
    requestTestNotification: bool = Field(None, description="Set to true by the AF to request the NEF to send a test notification as defined in clause 5.2.5.3 of 3GPP TS 29.122. Set to false or omitted otherwise.")
    websockNotifConfig: WebsockNotifConfig

class AnalyticsExposureSubsc(AnalyticsExposureSubscCreate):
    """Represents an analytics exposure subscription."""
    link: Optional[AnyHttpUrl] = Field("https://myresource.com", description="String identifying a referenced resource. This is also returned as a location header in 201 Created Response")
    class Config:
            orm_mode = True