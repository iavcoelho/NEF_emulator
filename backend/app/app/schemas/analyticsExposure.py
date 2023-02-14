from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress, AnyHttpUrl, constr
from enum import Enum
from .commonData import Snssai, TimeWindow, FlowInfo

############### TS 29.520 Types ###############

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
    #TODO: ts 29.520 TopApplication
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
    #TODO: ts 29.520 Exception
    excep: List[Exception]
    ratio: int = Field(None, description="Expressed in percent", ge=1, le=100)
    confidence: int = Field(None, description="", ge=0)
    #TODO: ts 29.520 AdditionalMeasurement
    addtMeasInfo: AdditionalMeasurement


class NetworkPerfExposure(BaseModel):
    """Represents network performance information."""
    locArea: LocationArea5G
    #TODO: ts 29.520 NetworkPerfType
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
    locArea: LocationArea5G
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