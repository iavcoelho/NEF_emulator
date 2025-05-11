from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Union
from typing_extensions import Annotated

from ipaddress import IPv4Address, IPv6Address

from pydantic import AnyHttpUrl, AnyUrl, Field

from .utils import ExtraBaseModel
from .commonData import (
    ExternalId,
    Msisdn,
    Snssai,
    Dnn,
    MacAddr48,
    Uinteger,
    SupportedFeatures,
    Gpsi,
    BitRate,
    Volume,
    PlmnId,
    Tai,
    Ecgi,
    GlobalRanNodeId,
    Ncgi,
    DurationMin,
    UserLocation,
    DurationSec,
    ExternalGroupId,
    WebsockNotifConfig,
    IpAddr,
)

# Shared properties | used for request body in endpoint/items.py
# We can declare a UserBase model that serves as a base for our other models. And then we can make subclasses of that model that inherit its attributes

ApplicationId = Annotated[
    str, Field(description="String providing an application identifier.")
]


Ipv6Prefix = Annotated[
    str,
    Field(
        description="String identifying an IPv6 address prefix formatted according to clause 4 of RFC 5952. IPv6Prefix data type may contain an individual /128 IPv6 address.",
    ),
]


Uncertainty = Annotated[
    float, Field(ge=0.0, description="Indicates value of uncertainty.")
]

Altitude = Annotated[
    float, Field(ge=-32767.0, le=32767.0, description="Indicates value of altitude.")
]

InnerRadius = Annotated[
    int, Field(ge=0, le=327675, description="Indicates value of the inner radius.")
]

Confidence = Annotated[
    int, Field(ge=0, le=100, description="Indicates value of confidence.")
]

Angle = Annotated[int, Field(ge=0, le=360, description="Indicates value of angle.")]

Orientation = Annotated[
    int, Field(ge=0, le=180, description="Indicates value of orientation angle.")
]

HorizontalSpeed = Annotated[
    float, Field(ge=0.0, le=2047.0, description="Indicates value of horizontal speed.")
]

VerticalSpeed = Annotated[
    float, Field(ge=0.0, le=255.0, description="Indicates value of vertical speed.")
]

SpeedUncertainty = Annotated[
    float, Field(ge=0.0, le=255.0, description="Indicates value of speed uncertainty.")
]

Accuracy = Annotated[float, Field(ge=0.0, description="Indicates value of accuracy.")]

ApplicationlayerId = Annotated[
    str,
    Field(
        description="String identifying an UE with application layer ID. The format of the application  layer ID parameter is same as the Application layer ID defined in clause 11.3.4 of  3GPP TS 24.554.",
    ),
]

Mcc = Annotated[
    str,
    Field(
        regex=r"^\d{3}$",
        description="Mobile Country Code part of the PLMN, comprising 3 digits, as defined in clause 9.3.3.5 of 3GPP TS 38.413.",
    ),
]


class SupportedGADShapes(str, Enum):
    POINT = "POINT"
    POINT_UNCERTAINTY_CIRCLE = "POINT_UNCERTAINTY_CIRCLE"
    POINT_UNCERTAINTY_ELLIPSE = "POINT_UNCERTAINTY_ELLIPSE"
    POLYGON = "POLYGON"
    POINT_ALTITUDE = "POINT_ALTITUDE"
    POINT_ALTITUDE_UNCERTAINTY = "POINT_ALTITUDE_UNCERTAINTY"
    ELLIPSOID_ARC = "ELLIPSOID_ARC"
    LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE = "LOCAL_2D_POINT_UNCERTAINTY_ELLIPSE"
    LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID = "LOCAL_3D_POINT_UNCERTAINTY_ELLIPSOID"
    DISTANCE_DIRECTION = "DISTANCE_DIRECTION"
    RELATIVE_2D_LOCATION_UNCERTAINTY_ELLIPSE = (
        "RELATIVE_2D_LOCATION_UNCERTAINTY_ELLIPSE"
    )
    RELATIVE_3D_LOCATION_UNCERTAINTY_ELLIPSOID = (
        "RELATIVE_3D_LOCATION_UNCERTAINTY_ELLIPSOID"
    )


class GADShape(ExtraBaseModel):
    shape: SupportedGADShapes


class GeographicalCoordinates(ExtraBaseModel):
    lon: Annotated[float, Field(ge=-180.0, le=180.0)]
    lat: Annotated[float, Field(ge=-90.0, le=90.0)]


PointList = Annotated[
    List[GeographicalCoordinates],
    Field(description="List of points.", max_items=15, min_items=3),
]


class Point(GADShape):
    point: GeographicalCoordinates


class PointUncertaintyCircle(GADShape):
    point: GeographicalCoordinates
    uncertainty: Uncertainty


class Polygon(GADShape):
    pointList: PointList


class PointAltitude(GADShape):
    point: GeographicalCoordinates
    altitude: Altitude


class EllipsoidArc(GADShape):
    point: GeographicalCoordinates
    innerRadius: InnerRadius
    uncertaintyRadius: Uncertainty
    offsetAngle: Angle
    includedAngle: Angle
    confidence: Confidence


class UncertaintyEllipse(ExtraBaseModel):
    semiMajor: Uncertainty
    semiMinor: Uncertainty
    orientationMajor: Orientation


class PointUncertaintyEllipse(GADShape):
    point: GeographicalCoordinates
    uncertaintyEllipse: UncertaintyEllipse
    confidence: Confidence


class PointAltitudeUncertainty(GADShape):
    point: GeographicalCoordinates
    altitude: Altitude
    uncertaintyEllipse: UncertaintyEllipse
    uncertaintyAltitude: Uncertainty
    confidence: Confidence
    vConfidence: Optional[Confidence] = None


GeographicArea = Annotated[
        Union[
            Point,
            PointUncertaintyCircle,
            PointUncertaintyEllipse,
            Polygon,
            PointAltitude,
            PointAltitudeUncertainty,
            EllipsoidArc,
        ],
        Field(description="Geographic area specified by different shape."),
    ]


class CivicAddress(ExtraBaseModel):
    country: Optional[str] = None
    A1: Optional[str] = None
    A2: Optional[str] = None
    A3: Optional[str] = None
    A4: Optional[str] = None
    A5: Optional[str] = None
    A6: Optional[str] = None
    PRD: Optional[str] = None
    POD: Optional[str] = None
    STS: Optional[str] = None
    HNO: Optional[str] = None
    HNS: Optional[str] = None
    LMK: Optional[str] = None
    LOC: Optional[str] = None
    NAM: Optional[str] = None
    PC: Optional[str] = None
    BLD: Optional[str] = None
    UNIT: Optional[str] = None
    FLR: Optional[str] = None
    ROOM: Optional[str] = None
    PLC: Optional[str] = None
    PCN: Optional[str] = None
    POBOX: Optional[str] = None
    ADDCODE: Optional[str] = None
    SEAT: Optional[str] = None
    RD: Optional[str] = None
    RDSEC: Optional[str] = None
    RDBR: Optional[str] = None
    RDSUBBR: Optional[str] = None
    PRM: Optional[str] = None
    POM: Optional[str] = None
    usageRules: Optional[str] = None
    method: Optional[str] = None
    providedBy: Optional[str] = None


class PositioningMethod(Enum):
    CELLID = "CELLID"
    ECID = "ECID"
    OTDOA = "OTDOA"
    BAROMETRIC_PRESSURE = "BAROMETRIC_PRESSURE"
    WLAN = "WLAN"
    BLUETOOTH = "BLUETOOTH"
    MBS = "MBS"
    MOTION_SENSOR = "MOTION_SENSOR"
    DL_TDOA = "DL_TDOA"
    DL_AOD = "DL_AOD"
    MULTI_RTT = "MULTI-RTT"
    NR_ECID = "NR_ECID"
    UL_TDOA = "UL_TDOA"
    UL_AOA = "UL_AOA"
    NETWORK_SPECIFIC = "NETWORK_SPECIFIC"
    SL_TDOA = "SL_TDOA"
    SL_TOA = "SL_TOA"
    SL_AoA = "SL_AoA"
    SL_RT = "SL_RT"


class AccuracyFulfilmentIndicator(Enum):
    REQUESTED_ACCURACY_FULFILLED = "REQUESTED_ACCURACY_FULFILLED"
    REQUESTED_ACCURACY_NOT_FULFILLED = "REQUESTED_ACCURACY_NOT_FULFILLED"


class VerticalDirection(Enum):
    UPWARD = "UPWARD"
    DOWNWARD = "DOWNWARD"


class HorizontalVelocity(ExtraBaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle


class HorizontalWithVerticalVelocity(ExtraBaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle
    vSpeed: VerticalSpeed
    vDirection: VerticalDirection


class HorizontalVelocityWithUncertainty(ExtraBaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle
    hUncertainty: SpeedUncertainty


class HorizontalWithVerticalVelocityAndUncertainty(ExtraBaseModel):
    hSpeed: HorizontalSpeed
    bearing: Angle
    vSpeed: VerticalSpeed
    vDirection: VerticalDirection
    hUncertainty: SpeedUncertainty
    vUncertainty: SpeedUncertainty


class VelocityEstimate(ExtraBaseModel):
    __root__: Annotated[
        Union[
            HorizontalVelocity,
            HorizontalWithVerticalVelocity,
            HorizontalVelocityWithUncertainty,
            HorizontalWithVerticalVelocityAndUncertainty,
        ],
        Field(description="Velocity estimate."),
    ]


class LdrType(Enum):
    UE_AVAILABLE = "UE_AVAILABLE"
    PERIODIC = "PERIODIC"
    ENTERING_INTO_AREA = "ENTERING_INTO_AREA"
    LEAVING_FROM_AREA = "LEAVING_FROM_AREA"
    BEING_INSIDE_AREA = "BEING_INSIDE_AREA"
    MOTION = "MOTION"


class MinorLocationQoS(ExtraBaseModel):
    hAccuracy: Optional[Accuracy] = None
    vAccuracy: Optional[Accuracy] = None


class RangeDirection(ExtraBaseModel):
    distance: Optional[float] = None
    azimuthDirection: Optional[Angle] = None
    elevationDirection: Optional[Angle] = None


class Field2DRelativeLocation(ExtraBaseModel):
    semiMinor: Optional[Uncertainty] = None
    semiMajor: Optional[Uncertainty] = None
    orientationAngle: Optional[Angle] = None


class Field3DRelativeLocation(ExtraBaseModel):
    semiMinor: Optional[Uncertainty] = None
    semiMajor: Optional[Uncertainty] = None
    verticalUncertainty: Optional[Uncertainty] = None
    orientationAngle: Optional[Angle] = None


class UpCumEvtRep(ExtraBaseModel):
    upLocRepStat: Optional[Uinteger] = None


class LocationInfo(ExtraBaseModel):
    ageOfLocationInfo: Optional[DurationMin] = None
    cellId: Annotated[
        Optional[str],
        Field(
            description="Indicates the Cell Global Identification of the user which identifies the cell the UE is registered.\n",
        ),
    ] = None
    enodeBId: Annotated[
        Optional[str],
        Field(description="Indicates the eNodeB in which the UE is currently located."),
    ] = None
    routingAreaId: Annotated[
        Optional[str],
        Field(
            description="Identifies the Routing Area Identity of the user where the UE is located.",
        ),
    ] = None
    trackingAreaId: Annotated[
        Optional[str],
        Field(
            description="Identifies the Tracking Area Identity of the user where the UE is located.",
        ),
    ] = None
    plmnId: Annotated[
        Optional[str],
        Field(
            description="Identifies the PLMN Identity of the user where the UE is located.",
        ),
    ] = None
    twanId: Annotated[
        Optional[str],
        Field(
            description="Identifies the TWAN Identity of the user where the UE is located.",
        ),
    ] = None
    userLocation: Optional[UserLocation] = None
    geographicArea: Optional[GeographicArea] = None
    civicAddress: Optional[CivicAddress] = None
    positionMethod: Optional[PositioningMethod] = None
    qosFulfilInd: Optional[AccuracyFulfilmentIndicator] = None
    ueVelocity: Optional[VelocityEstimate] = None
    ldrType: Optional[LdrType] = None
    achievedQos: Optional[MinorLocationQoS] = None
    relAppLayerId: Optional[ApplicationlayerId] = None
    rangeDirection: Optional[RangeDirection] = None
    twoDRelLoc: Optional[Field2DRelativeLocation] = None
    threeDRelLoc: Optional[Field3DRelativeLocation] = None
    relVelocity: Optional[VelocityEstimate] = None
    upCumEvtRep: Optional[UpCumEvtRep] = None


class MonitoringType(str, Enum):
    LOSS_OF_CONNECTIVITY = "LOSS_OF_CONNECTIVITY"
    UE_REACHABILITY = "UE_REACHABILITY"
    LOCATION_REPORTING = "LOCATION_REPORTING"
    CHANGE_OF_IMSI_IMEI_ASSOCIATION = "CHANGE_OF_IMSI_IMEI_ASSOCIATION"
    ROAMING_STATUS = "ROAMING_STATUS"
    COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"
    AVAILABILITY_AFTER_DDN_FAILURE = "AVAILABILITY_AFTER_DDN_FAILURE"
    NUMBER_OF_UES_IN_AN_AREA = "NUMBER_OF_UES_IN_AN_AREA"
    PDN_CONNECTIVITY_STATUS = "PDN_CONNECTIVITY_STATUS"
    DOWNLINK_DATA_DELIVERY_STATUS = "DOWNLINK_DATA_DELIVERY_STATUS"
    API_SUPPORT_CAPABILITY = "API_SUPPORT_CAPABILITY"
    NUM_OF_REGD_UES = "NUM_OF_REGD_UES"
    NUM_OF_ESTD_PDU_SESSIONS = "NUM_OF_ESTD_PDU_SESSIONS"
    AREA_OF_INTEREST = "AREA_OF_INTEREST"
    GROUP_MEMBER_LIST_CHANGE = "GROUP_MEMBER_LIST_CHANGE"
    APPLICATION_START = "APPLICATION_START"
    APPLICATION_STOP = "APPLICATION_STOP"
    SESSION_INACTIVITY_TIME = "SESSION_INACTIVITY_TIME"
    TRAFFIC_VOLUME = "TRAFFIC_VOLUME"
    UL_DL_DATA_RATE = "UL_DL_DATA_RATE"


class ReachabilityType(str, Enum):
    SMS = "SMS"
    DATA = "DATA"


class AssociationTypeModel(str, Enum):
    IMEI = "IMEI"
    IMEISV = "IMEISV"


class PduSessionInformation(ExtraBaseModel):
    snssai: Snssai
    dnn: Dnn
    ueIpv4: Optional[IPv4Address] = None
    ueIpv6: Optional[IPv6Address] = None
    ipDomain: Optional[str] = None
    ueMac: Optional[MacAddr48] = None


class IdleStatusInfo(ExtraBaseModel):
    activeTime: Optional[DurationSec] = None
    edrxCycleLength: Annotated[Optional[float], Field(ge=0.0)] = None
    suggestedNumberOfDlPackets: Annotated[
        Optional[int],
        Field(
            ge=0,
            description='Identifies the number of packets shall be buffered in the serving gateway. It shall be present if the idle status indication is requested by the SCS/AS with "idleStatusIndication" in the "monitoringEventSubscription" sets to "true".',
        ),
    ] = None
    idleStatusTimestamp: Optional[datetime] = None
    periodicAUTimer: Optional[DurationSec] = None


class LocationFailureCause(Enum):
    POSITIONING_DENIED = "POSITIONING_DENIED"
    UNSUPPORTED_BY_UE = "UNSUPPORTED_BY_UE"
    NOT_REGISTED_UE = "NOT_REGISTED_UE"
    UNSPECIFIED = "UNSPECIFIED"
    REQUESTED_AREA_NOT_ALLOWED = "REQUESTED_AREA_NOT_ALLOWED"


class UePerLocationReport(ExtraBaseModel):
    ueCount: Annotated[int, Field(ge=0, description="Identifies the number of UEs.")]
    externalIds: Annotated[
        Optional[List[ExternalId]],
        Field(description="Each element uniquely identifies a user.", min_items=1),
    ] = None
    msisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description="Each element identifies the MS internal PSTN/ISDN number allocated for a UE.",
            min_items=1,
        ),
    ] = None
    servLevelDevIds: Annotated[
        Optional[List[str]],
        Field(description="Each element uniquely identifies a UAV.", min_items=1),
    ] = None


class FailureCause(ExtraBaseModel):
    bssgpCause: Annotated[
        Optional[int],
        Field(
            description="Identifies a non-transparent copy of the BSSGP cause code. Refer to 3GPP TS 29.128.",
        ),
    ] = None
    causeType: Annotated[
        Optional[int],
        Field(
            description="Identify the type of the S1AP-Cause. Refer to 3GPP TS 29.128.",
        ),
    ] = None
    gmmCause: Annotated[
        Optional[int],
        Field(
            description="Identifies a non-transparent copy of the GMM cause code. Refer to 3GPP TS 29.128.",
        ),
    ] = None
    ranapCause: Annotated[
        Optional[int],
        Field(
            description="Identifies a non-transparent copy of the RANAP cause code. Refer to 3GPP TS 29.128.",
        ),
    ] = None
    ranNasCause: Annotated[
        Optional[str],
        Field(
            description="Indicates RAN and/or NAS release cause code information, TWAN release cause code information or untrusted WLAN release cause code information. Refer to 3GPP TS 29.214.",
        ),
    ] = None
    s1ApCause: Annotated[
        Optional[int],
        Field(
            description="Identifies a non-transparent copy of the S1AP cause code. Refer to 3GPP TS 29.128.",
        ),
    ] = None
    smCause: Annotated[
        Optional[int],
        Field(
            description="Identifies a non-transparent copy of the SM cause code. Refer to 3GPP TS 29.128.",
        ),
    ] = None


class PdnConnectionStatus(Enum):
    CREATED = "CREATED"
    RELEASED = "RELEASED"


class PdnType(Enum):
    IPV4 = "IPV4"
    IPV6 = "IPV6"
    IPV4V6 = "IPV4V6"
    NON_IP = "NON_IP"
    ETHERNET = "ETHERNET"


class InterfaceIndication(Enum):
    EXPOSURE_FUNCTION = "EXPOSURE_FUNCTION"
    PDN_GATEWAY = "PDN_GATEWAY"


class PdnConnectionInformation(ExtraBaseModel):
    status: PdnConnectionStatus
    apn: Annotated[
        Optional[str],
        Field(
            description="Identify the APN, it is depending on the SCEF local configuration whether or not this attribute is sent to the SCS/AS.",
        ),
    ] = None
    pdnType: PdnType
    interfaceInd: Optional[InterfaceIndication] = None
    ipv4Addr: Optional[IPv4Address] = None
    ipv6Addrs: Annotated[Optional[List[IPv6Address]], Field(min_items=1)] = None
    macAddrs: Annotated[Optional[List[MacAddr48]], Field(min_items=1)] = None


class DlDataDeliveryStatus(str, Enum):
    BUFFERED = "BUFFERED"
    TRANSMITTED = "TRANSMITTED"
    DISCARDED = "DISCARDED"


class DddTrafficDescriptor(ExtraBaseModel):
    ipv4Addr: Optional[IPv4Address] = None
    ipv6Addr: Optional[IPv6Address] = None
    portNumber: Optional[Uinteger] = None
    macAddr: Optional[MacAddr48] = None


class ApiCapabilityInfo(ExtraBaseModel):
    apiName: str
    suppFeat: SupportedFeatures


class SACInfo(ExtraBaseModel):
    numericValNumUes: Optional[int] = None
    numericValNumPduSess: Optional[int] = None
    percValueNumUes: Annotated[Optional[int], Field(ge=0, le=100)] = None
    percValueNumPduSess: Annotated[Optional[int], Field(ge=0, le=100)] = None
    uesWithPduSessionInd: Optional[bool] = False


class SACEventStatus(ExtraBaseModel):
    reachedNumUes: Optional[SACInfo] = None
    reachedNumPduSess: Optional[SACInfo] = None


class GroupMembListChanges(ExtraBaseModel):
    addedUEs: Annotated[Optional[List[Gpsi]], Field(min_items=1)] = None
    removedUEs: Annotated[Optional[List[Gpsi]], Field(min_items=1)] = None


class TrafficInformation(ExtraBaseModel):
    uplinkRate: Optional[BitRate] = None
    downlinkRate: Optional[BitRate] = None
    uplinkVolume: Optional[Volume] = None
    downlinkVolume: Optional[Volume] = None
    totalVolume: Optional[Volume] = None


class MonitoringEventReport(ExtraBaseModel):
    imeiChange: Optional[AssociationTypeModel] = None
    externalId: Optional[ExternalId] = None
    appId: Optional[ApplicationId] = None
    pduSessInfo: Optional[PduSessionInformation] = None
    idleStatusInfo: Optional[IdleStatusInfo] = None
    locationInfo: Optional[LocationInfo] = None
    locFailureCause: Optional[LocationFailureCause] = None
    lossOfConnectReason: Annotated[
        Optional[int],
        Field(
            description='If "monitoringType" is "LOSS_OF_CONNECTIVITY", this parameter shall be included if available to identify the reason why loss of connectivity is reported. Refer to 3GPP TS 29.336 clause 8.4.58.',
        ),
    ] = None
    unavailPerDur: Optional[DurationSec] = None
    maxUEAvailabilityTime: Optional[datetime] = None
    msisdn: Optional[Msisdn] = None
    monitoringType: MonitoringType
    uePerLocationReport: Optional[UePerLocationReport] = None
    plmnId: Optional[PlmnId] = None
    reachabilityType: Optional[ReachabilityType] = None
    roamingStatus: Annotated[
        Optional[bool],
        Field(
            description='If "monitoringType" is "ROAMING_STATUS", this parameter shall be set to "true" if the new serving PLMN is different from the HPLMN. Set to false or omitted otherwise.',
        ),
    ] = None
    failureCause: Optional[FailureCause] = None
    eventTime: Optional[datetime] = None
    pdnConnInfoList: Annotated[
        Optional[List[PdnConnectionInformation]], Field(min_items=1)
    ] = None
    dddStatus: Optional[DlDataDeliveryStatus] = None
    dddTrafDescriptor: Optional[DddTrafficDescriptor] = None
    maxWaitTime: Optional[datetime] = None
    apiCaps: Annotated[Optional[List[ApiCapabilityInfo]], Field(min_items=0)] = None
    nSStatusInfo: Optional[SACEventStatus] = None
    afServiceId: Optional[str] = None
    servLevelDevId: Annotated[
        Optional[str],
        Field(
            description='If "monitoringType" is "AREA_OF_INTEREST", this parameter may be included to identify the UAV.',
        ),
    ] = None
    uavPresInd: Annotated[
        Optional[bool],
        Field(
            description='If "monitoringType" is "AREA_OF_INTEREST", this parameter shall be set to true if the specified UAV is in the monitoring area. Set to false or omitted otherwise.',
        ),
    ] = None
    groupMembListChanges: Optional[GroupMembListChanges] = None
    sessInactiveTime: Optional[DurationSec] = None
    trafficInfo: Optional[TrafficInformation] = None


class ResultReason(Enum):
    ROAMING_NOT_ALLOWED = "ROAMING_NOT_ALLOWED"
    OTHER_REASON = "OTHER_REASON"


class ConfigResult(ExtraBaseModel):
    externalIds: Annotated[
        Optional[List[ExternalId]],
        Field(
            description="Each element indicates an external identifier of the UE.",
            min_items=1,
        ),
    ] = None
    msisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description="Each element identifies the MS internal PSTN/ISDN number allocated for the UE.",
            min_items=1,
        ),
    ] = None
    resultReason: ResultReason


class AppliedParameterConfiguration(ExtraBaseModel):
    externalIds: Annotated[
        Optional[List[ExternalId]],
        Field(description="Each element uniquely identifies a user.", min_items=1),
    ] = None
    msisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description="Each element identifies the MS internal PSTN/ISDN number allocated for a UE.",
            min_items=1,
        ),
    ] = None
    maximumLatency: Optional[DurationSec] = None
    maximumResponseTime: Optional[DurationSec] = None
    maximumDetectionTime: Optional[DurationSec] = None


class MonitoringNotification(ExtraBaseModel):
    subscription: AnyHttpUrl
    configResults: Annotated[
        Optional[List[ConfigResult]],
        Field(
            description="Each element identifies a notification of grouping configuration result.",
            min_items=1,
        ),
    ] = None
    monitoringEventReports: Annotated[
        Optional[List[MonitoringEventReport]],
        Field(description="Monitoring event reports.", min_items=1),
    ] = None
    addedExternalIds: Annotated[
        Optional[List[ExternalId]],
        Field(
            description='Identifies the added external Identifier(s) within the active group via the "externalGroupId" attribute within the MonitoringEventSubscription data type.',
            min_items=1,
        ),
    ] = None
    addedMsisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description='Identifies the added MSISDN(s) within the active group via the "externalGroupId" attribute within the MonitoringEventSubscription data type.',
            min_items=1,
        ),
    ] = None
    cancelExternalIds: Annotated[
        Optional[List[ExternalId]],
        Field(
            description='Identifies the cancelled external Identifier(s) within the active group via the "externalGroupId" attribute within the MonitoringEventSubscription data type.',
            min_items=1,
        ),
    ] = None
    cancelMsisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description='Identifies the cancelled MSISDN(s) within the active group via the "externalGroupId" attribute within the MonitoringEventSubscription data type.',
            min_items=1,
        ),
    ] = None
    cancelInd: Annotated[
        Optional[bool],
        Field(
            description="Indicates whether to request to cancel the corresponding monitoring subscription. Set to false or omitted otherwise.",
        ),
    ] = None
    appliedParam: Optional[AppliedParameterConfiguration] = None


class LocationType(str, Enum):
    CURRENT_LOCATION = "CURRENT_LOCATION"
    LAST_KNOWN_LOCATION = "LAST_KNOWN_LOCATION"
    CURRENT_OR_LAST_KNOWN_LOCATION = "CURRENT_OR_LAST_KNOWN_LOCATION"
    INITIAL_LOCATION = "INITIAL_LOCATION"


class AccuracyModel(str, Enum):
    CGI_ECGI = "CGI_ECGI"
    ENODEB = "ENODEB"
    TA_RA = "TA_RA"
    PLMN = "PLMN"
    TWAN_ID = "TWAN_ID"
    GEO_AREA = "GEO_AREA"
    CIVIC_ADDR = "CIVIC_ADDR"


class ResponseTime(str, Enum):
    LOW_DELAY = "LOW_DELAY"
    DELAY_TOLERANT = "DELAY_TOLERANT"
    NO_DELAY = "NO_DELAY"


class LcsQosClass(str, Enum):
    BEST_EFFORT = "BEST_EFFORT"
    ASSURED = "ASSURED"
    MULTIPLE_QOS = "MULTIPLE_QOS"


class LocationQoS(ExtraBaseModel):
    hAccuracy: Optional[Accuracy] = None
    vAccuracy: Optional[Accuracy] = None
    verticalRequested: Optional[bool] = None
    responseTime: Optional[ResponseTime] = None
    minorLocQoses: Annotated[
        Optional[List[MinorLocationQoS]], Field(max_items=2, min_items=1)
    ] = None
    lcsQosClass: Optional[LcsQosClass] = None


LinearDistance = Annotated[
    int,
    Field(
        ge=1,
        le=10000,
        description="Minimum straight line distance moved by a UE to trigger a motion event report.",
    ),
]


ServiceIdentity = Annotated[str, Field(description="Contains the service identity")]


Fqdn = Annotated[
    str,
    Field(
        regex=r"^([0-9A-Za-z]([-0-9A-Za-z]{0,61}[0-9A-Za-z])?\.)+[A-Za-z]{2,63}\.?$",
        min_length=4,
        max_length=253,
        description="Fully Qualified Domain Name",
    ),
]


class UpLocRepAddrAfRm(ExtraBaseModel):
    ipv4Addrs: Annotated[Optional[List[IPv4Address]], Field(min_items=1)] = None
    ipv6Addrs: Annotated[Optional[List[IPv6Address]], Field(min_items=1)] = None
    fqdn: Optional[Fqdn] = None


CodeWord = Annotated[str, Field(description="Contains the codeword")]


class NetworkAreaInfo(ExtraBaseModel):
    ecgis: Annotated[
        Optional[List[Ecgi]],
        Field(description="Contains a list of E-UTRA cell identities.", min_items=1),
    ] = None
    ncgis: Annotated[
        Optional[List[Ncgi]],
        Field(description="Contains a list of NR cell identities.", min_items=1),
    ] = None
    gRanNodeIds: Annotated[
        Optional[List[GlobalRanNodeId]],
        Field(description="Contains a list of NG RAN nodes.", min_items=1),
    ] = None
    tais: Annotated[
        Optional[List[Tai]],
        Field(description="Contains a list of tracking area identities.", min_items=1),
    ] = None


class RelatedUeType(str, Enum):
    LOCATED_UE = "LOCATED_UE"
    REFERENCE_UE = "REFERENCE_UE"


class RelatedUeModel(ExtraBaseModel):
    applicationlayerId: ApplicationlayerId
    relatedUeType: RelatedUeType


class RangingSlResult(str, Enum):
    ABSOLUTE_LOCATION = "ABSOLUTE_LOCATION"
    RELATIVE_LOCATION = "RELATIVE_LOCATION"
    RANGING_DIRECTION = "RANGING_DIRECTION"
    RANGING = "RANGING"
    DIRECTION = "DIRECTION"
    VELOCITY = "VELOCITY"
    RELATIVE_VELOCITY = "RELATIVE_VELOCITY"


class SubType(str, Enum):
    AERIAL_UE = "AERIAL_UE"


class UavPolicy(ExtraBaseModel):
    uavMoveInd: bool
    revokeInd: bool


class SACRepFormat(str, Enum):
    NUMERICAL = "NUMERICAL"
    PERCENTAGE = "PERCENTAGE"


class LocationArea5G(ExtraBaseModel):
    geographicAreas: Annotated[
        Optional[List[GeographicArea]],
        Field(
            description="Identifies a list of geographic area of the user where the UE is located.",
            min_items=0,
        ),
    ] = None
    civicAddresses: Annotated[
        Optional[List[CivicAddress]],
        Field(
            description="Identifies a list of civic addresses of the user where the UE is located.",
            min_items=0,
        ),
    ] = None
    nwAreaInfo: Optional[NetworkAreaInfo] = None


class LocationArea(ExtraBaseModel):
    cellIds: Annotated[
        Optional[List[str]],
        Field(
            description="Indicates a list of Cell Global Identities of the user which identifies the cell the UE is registered.",
            min_items=1,
        ),
    ] = None
    enodeBIds: Annotated[
        Optional[List[str]],
        Field(
            description="Indicates a list of eNodeB identities in which the UE is currently located.",
            min_items=1,
        ),
    ] = None
    routingAreaIds: Annotated[
        Optional[List[str]],
        Field(
            description="Identifies a list of Routing Area Identities of the user where the UE is located.",
            min_items=1,
        ),
    ] = None
    trackingAreaIds: Annotated[
        Optional[List[str]],
        Field(
            description="Identifies a list of Tracking Area Identities of the user where the UE is located.",
            min_items=1,
        ),
    ] = None
    geographicAreas: Annotated[
        Optional[List[GeographicArea]],
        Field(
            description="Identifies a list of geographic area of the user where the UE is located.",
            min_items=1,
        ),
    ] = None
    civicAddresses: Annotated[
        Optional[List[CivicAddress]],
        Field(
            description="Identifies a list of civic addresses of the user where the UE is located.",
            min_items=1,
        ),
    ] = None


class VelocityRequested(str, Enum):
    VELOCITY_IS_NOT_REQUESTED = "VELOCITY_IS_NOT_REQUESTED"
    VELOCITY_IS_REQUESTED = "VELOCITY_IS_REQUESTED"


AgeOfLocationEstimate = Annotated[
    int,
    Field(
        ge=0,
        le=32767,
        description="Indicates value of the age of the location estimate.",
    ),
]


class TimeWindowModel(ExtraBaseModel):
    startTime: datetime
    stopTime: datetime


class MonitoringEventSubscription(ExtraBaseModel):
    self: Optional[AnyUrl] = None
    supportedFeatures: Optional[SupportedFeatures] = None
    mtcProviderId: Annotated[
        Optional[str],
        Field(
            description="Identifies the MTC Service Provider and/or MTC Application."
        ),
    ] = None
    appIds: Annotated[
        Optional[List[str]],
        Field(description="Identifies the Application Identifier(s)", min_items=1),
    ] = None
    externalId: Optional[ExternalId] = None
    msisdn: Optional[Msisdn] = None
    addedExternalIds: Annotated[
        Optional[List[ExternalId]],
        Field(
            description="Indicates the added external Identifier(s) within the active group.",
            min_items=1,
        ),
    ] = None
    addedMsisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description="Indicates the added MSISDN(s) within the active group.",
            min_items=1,
        ),
    ] = None
    excludedExternalIds: Annotated[
        Optional[List[ExternalId]],
        Field(
            description="Indicates cancellation of the external Identifier(s) within the active group.",
            min_items=1,
        ),
    ] = None
    excludedMsisdns: Annotated[
        Optional[List[Msisdn]],
        Field(
            description="Indicates cancellation of the MSISDN(s) within the active group.",
            min_items=1,
        ),
    ] = None
    externalGroupId: Optional[ExternalGroupId] = None
    addExtGroupId: Annotated[Optional[List[ExternalGroupId]], Field(min_items=2)] = None
    ipv4Addr: Optional[IPv4Address] = None
    ipv6Addr: Optional[IPv6Address] = None
    dnn: Optional[Dnn] = None
    notificationDestination: AnyUrl
    requestTestNotification: Annotated[
        Optional[bool],
        Field(
            description="Set to true by the SCS/AS to request the SCEF to send a test notification as defined in clause 5.2.5.3. Set to false by the SCS/AS indicates not request SCEF to send a test notification, default false if omitted otherwise.",
        ),
    ] = None
    websockNotifConfig: Optional[WebsockNotifConfig] = None
    monitoringType: MonitoringType
    maximumNumberOfReports: Annotated[
        Optional[int],
        Field(
            ge=1,
            description="Identifies the maximum number of event reports to be generated by the HSS, MME/SGSN as specified in clause 5.6.0 of 3GPP TS 23.682.",
        ),
    ] = None
    monitorExpireTime: Optional[datetime] = None
    repPeriod: Optional[DurationSec] = None
    groupReportGuardTime: Optional[DurationSec] = None
    maximumDetectionTime: Optional[DurationSec] = None
    reachabilityType: Optional[ReachabilityType] = None
    maximumLatency: Optional[DurationSec] = None
    maximumResponseTime: Optional[DurationSec] = None
    suggestedNumberOfDlPackets: Annotated[
        Optional[int],
        Field(
            ge=0,
            description='If "monitoringType" is "UE_REACHABILITY", this parameter may be included to identify the number of packets that the serving gateway shall buffer in case that the UE is not reachable.',
        ),
    ] = None
    idleStatusIndication: Annotated[
        Optional[bool],
        Field(
            description='If "monitoringType" is set to "UE_REACHABILITY" or "AVAILABILITY_AFTER_DDN_FAILURE", this parameter may be included to indicate the notification of when a UE, for which PSM is enabled, transitions into idle mode. "true"  indicates enabling of notification; "false"  indicate no need to notify. Default value is "false" if omitted.',
        ),
    ] = None
    locationType: Optional[LocationType] = None
    accuracy: Optional[AccuracyModel] = None
    minimumReportInterval: Optional[DurationSec] = None
    maxRptExpireIntvl: Optional[DurationSec] = None
    samplingInterval: Optional[DurationSec] = None
    reportingLocEstInd: Annotated[
        Optional[bool],
        Field(
            description='Indicates whether to request the location estimate for event reporting. If "monitoringType" is "LOCATION_REPORTING", this parameter may be included to indicate whether event reporting requires the location information. If set to true, the location estimation information shall be included in event reporting. If set to "false", indicates the location estimation information shall not be included in event reporting. Default "false" if omitted.',
        ),
    ] = None
    linearDistance: Optional[LinearDistance] = None
    locQoS: Optional[LocationQoS] = None
    svcId: Optional[ServiceIdentity] = None
    ldrType: Optional[LdrType] = None
    velocityRequested: Optional[VelocityRequested] = None
    maxAgeOfLocEst: Optional[AgeOfLocationEstimate] = None
    locTimeWindow: Optional[TimeWindowModel] = None
    supportedGADShapes: Optional[List[SupportedGADShapes]] = None
    codeWord: Optional[CodeWord] = None
    upLocRepIndAf: Annotated[
        bool,
        Field(
            description='Indicates whether location reporting over user plane is requested or not. "true" indicates the location reporting over user plane is requested. "false" indicates the location reporting over user plane is not requested. Default value is "false" if omitted.',
        ),
    ] = False
    upLocRepAddrAf: Optional[UpLocRepAddrAfRm] = None
    associationType: Optional[AssociationTypeModel] = None
    plmnIndication: Annotated[
        Optional[bool],
        Field(
            description='If "monitoringType" is "ROAMING_STATUS", this parameter may be included to indicate the notification of UE\'s Serving PLMN ID. Value "true" indicates enabling of notification; "false" indicates disabling of notification. Default value is "false" if omitted.',
        ),
    ] = None
    locationArea: Optional[LocationArea] = None
    locationArea5G: Optional[LocationArea5G] = None
    dddTraDescriptors: Annotated[
        Optional[List[DddTrafficDescriptor]], Field(min_items=1)
    ] = None
    dddStati: Annotated[Optional[List[DlDataDeliveryStatus]], Field(min_items=1)] = None
    apiNames: Annotated[Optional[List[str]], Field(min_items=1)] = None
    monitoringEventReport: Optional[MonitoringEventReport] = None
    snssai: Optional[Snssai] = None
    tgtNsThreshold: Optional[SACInfo] = None
    nsRepFormat: Optional[SACRepFormat] = None
    afServiceId: Optional[str] = None
    immediateRep: Annotated[
        Optional[bool],
        Field(
            description='Indicates whether an immediate reporting is requested or not. "true" indicate an immediate reporting is requested. "false" indicate an immediate reporting is not requested. Default value "false" if omitted.',
        ),
    ] = None
    uavPolicy: Optional[UavPolicy] = None
    sesEstInd: Annotated[
        Optional[bool],
        Field(
            description='Set to true by the SCS/AS so that only UAV\'s with "PDU session established for DNN(s) subject to aerial service" are to be listed in the Event report. Set to false or default false if omitted otherwise.',
        ),
    ] = None
    subType: Optional[SubType] = None
    addnMonTypes: Optional[List[MonitoringType]] = None
    addnMonEventReports: Optional[List[MonitoringEventReport]] = None
    ueIpAddr: Optional[IpAddr] = None
    ueMacAddr: Optional[MacAddr48] = None
    revocationNotifUri: Optional[AnyUrl] = None
    reqRangSlRes: Annotated[Optional[List[RangingSlResult]], Field(min_items=1)] = None
    relatedUes: Annotated[
        Optional[Dict[str, RelatedUeModel]],
        Field(
            description="Contains a list of the related UE(s) for the ranging and sidelink positioning and the corresponding information. The key of the map shall be a any unique string set to the value.",
        ),
    ] = None
