# SystemLink Test Monitor results example

This is an example of uploading test results to the SystemLink Test Monitor service.
It simulates measuring the power output from a device and tests the measured power
to ensure it is within a specified upper and lower limit.  The power is simulated using
the simple electrical equation `P=VI` (power=voltage*current).  In this example, a random
amount of current loss and voltage loss are induced to simulate a non-ideal device.

A top level result is created containing metadata about the overall test.

The example sweeps across a range of input currents and voltages and takes measurements
for each combination. It then stores each single measurement within each test step.  The test
steps are associated with the test result, and in some cases, as child relationships
to other test steps.  Each step is uploaded to the SystemLink server as it is generated.

At the end, the step status is evaluated to set the status of the parent step and
ultimately sets the status of the top-level test result.

## Dependencies
- The **NI SystemLink Python SDK** must be installed on the system using the NI Package Manager.  The package is available when installing the SystemLink Server or Client.  The NI SystemLink Python SDK is installed under `C:\Program Files\National Instruments\Shared\Skyline\Python` and contains the test monitor client which this example imports.
