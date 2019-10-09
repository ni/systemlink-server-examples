# Asset examples

The **asset** folder contains examples that exercise the Asset Management APIs.

## Scripts

### **cpu_triggered_asset_utilization.py**

#### Description

Script used to automatically mark the system as utilized (or a subset of assets from the system) as long as the CPU utilization perecentage goes over a specified limit.

#### Requirements
This script only supports 64bit Windows systems. The script requires the "NI SystemLink Client" to be installed as it interacts with some components of it. For the same reason, the script should be run with the distribution of Python that comes with the "NI SystemLink Client".

#### How to run it

From a command line with administrator privileges run:

`"path-to-Program-Files-directory\National Instruments\Shared\salt-minion\bin\python.exe" cpu_triggered_asset_utilization.py`

Use the *-h* argument to see all possible script configurations.
