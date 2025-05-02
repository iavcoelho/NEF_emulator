# Quality of Service development documentation

## Introduction

`NEF_Emulator` supports integrating with a real 5G core to allow Quality of
Service interfaces, namely `Nnef_AFsessionWithQoS`, to change QoS flows of real
devices.

Since many cores don't support the standard 3gpp interfaces to influence QoS,
`NEF_Emulator` defines an interface (`AfSessionWithQosInterface`) in
`backend/app/app/interfaces/afSessionWithQos.py` that abstracts over different
implementations for different cores. These implementations are stored in
`backend/app/app/drivers/afSessionWithQos`.

## Creating a new implementation

First a driver must be implemented such that the implementation class inherits
from the `AfSessionWithQosInterface` and all abstract methods must be
implemented.

There are two main methods, one for applying and another for reverting QoS.
Both are given the subscription asking for the QoS change, and a list of UEs, a
list is given since the subscription supports specifying multiple devices at
once. Implementations can batch the request for all the UEs if supported, or
simply iterate over all UEs changing the QoS (either sequentially or in
parallel).

The apply operation is also given the QoS Profile characteristics, that are
either specified by the NEF client or by the QoS reference selected by the
client.

The revert operation is supposed to tear down the QoS applied by the
subscription, however some cores might not support this operation or track this
information. In that case implementations may choose to do nothing or apply a
default QoS profile whenever the QoS is reverted.

All the methods are `async` to ensure that the thread handling the QoS request
isn't stuck while waiting for the core to respond. This requires that all I/O
operations (e.g. network requests) be non-blocking, for example, all HTTP
requests should be made using `httpx` instead of `requests` since the latter is
blocking.

After the implementation class is created, it's necessary to define a new QoS
backend variant in the `QoSInterfaceBackend` enum located in
`backend/app/app/core/config.py`. This will allow the user to then select the
QoS backend through the `QOS__BACKEND` environment variable. If further
configuration is needed for the implementation (e.g. API URLs), they can be
added to the `QoSInterfaceSettings` class and then the settings variable can be
imported by the implementation.

Finally, the `backend/app/app/drivers/afSessionWithQos/__init__.py` needs to be
updated to instantiate the implementation when the backend enum variant is
selected.

## QoS profiles

Consumers of the NEF may opt to designate the QoS through a QoS reference,
these QoS references are mapped to profiles in the
`backend/app/app/core/config/qosCharacteristics.json` file, the file contains a
dictionary from QoS reference to QoS profile characteristics, namely
`uplinkBitRate`, `downlinkBitRate`, `packetDelayBudget`, and `packerErrRate`
(all characteristics are defined by the class `QoSProfile` in
`backend/app/app/core/config.py`).

The NEF must be restarted if the file is changed as reloading the file at
runtime isn't supported.
