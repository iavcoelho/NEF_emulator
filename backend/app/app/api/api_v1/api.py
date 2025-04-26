from fastapi import APIRouter

from app.api.api_v1 import endpoints

api_router = APIRouter()
api_router.include_router(endpoints.login.router, tags=["login"])
api_router.include_router(endpoints.users.router, prefix="/users", tags=["users"])
api_router.include_router(endpoints.utils.router, prefix="/utils", tags=["UI"])
api_router.include_router(endpoints.scenario.router, prefix="/utils", tags=["UI"])
api_router.include_router(endpoints.ue_movement.router, prefix="/ue_movement", tags=["Movement"])
api_router.include_router(endpoints.paths.router, prefix="/paths", tags=["Paths"])
api_router.include_router(endpoints.gNB.router, prefix="/gNBs", tags=["gNBs"])
api_router.include_router(endpoints.Cell.router, prefix="/Cells", tags=["Cells"])
api_router.include_router(endpoints.UE.router, prefix="/UEs", tags=["UEs"])
api_router.include_router(endpoints.qosInformation.router, prefix="/qosInfo", tags=["QoS Information"])


    # ---Create a subapp---
nef_router = APIRouter()
nef_router.include_router(endpoints.monitoringevent.router, prefix="/3gpp-monitoring-event/v1", tags=["Monitoring Event API"])
nef_router.include_router(endpoints.afSessionWithQoS.router, prefix="/3gpp-as-session-with-qos/v1", tags=["Session With QoS API"])
nef_router.include_router(endpoints.bdtManagement.router, prefix="/3gpp-bdt/v1", tags=["Resource Management of Bdt API"])
nef_router.include_router(endpoints.trafficInfluence.router, prefix="/3gpp-traffic-influence/v1", tags=["Traffic Influence API"])
nef_router.include_router(endpoints.chargeableParty.router, prefix="/3gpp-chargeable-party/v1", tags=["Chargeable Party API"])
nef_router.include_router(endpoints.netStatReport.router, prefix="/3gpp-net-stat-report/v1", tags=["Reporting Network Status API"])
nef_router.include_router(endpoints.cpParameterProvisioning.router, prefix="/3gpp-cp-parameter-provisioning/v1", tags=["Communication Patterns (CP) Parameters Provisioning API"])
nef_router.include_router(endpoints.pfdManagement.router, prefix="/3gpp-pfd-management/v1", tags=["Packet Flow Description (PFD) Management API"])
nef_router.include_router(endpoints.npConfiguration.router, prefix="/3gpp-network-parameter-configuration/v1", tags=["Network Parameter Configuration API"])
nef_router.include_router(endpoints.racsProvisioning.router, prefix="/3gpp-racs-pp/v1", tags=["RACS (Radio Capability Signaling) Parameter Provisioning API"])
nef_router.include_router(endpoints.analyticsExposure.router, prefix="/3gpp-analyticsexposure/v1", tags=["Analytics Exposure API"])

    # ---Create a subapp---
tests_router = APIRouter()
tests_router.include_router(endpoints.tests.router, prefix="/UEs", tags=["UE Tests"])
tests_router.include_router(endpoints.broker.router, prefix="/broker", tags=["Broker"])
