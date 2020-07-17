# SystemLink Test Monitor manual configuration example

This is an example of uploading a test result to the SystemLink Test Monitor service
using a manual configuration.  This is helpful when accessing the SystemLink server from
a device that is not registered with the server.

This example accepts command-line arguments to configure the connection to the SystemLink server.
The connection URL can be specified to connect to a specific SystemLink server.  Optionally,
the user can specify either an API key or a username and password to connect to the server.

Once a connection is configured, a simple test result (with no child steps) is created on
the server to validate that the connection information succeeds in accessing the server.

## Depenencies
- The **NI SystemLink Python SDK** must be installed on the system using the NI Package Manager.  The package is available when installing the SystemLink Server or Client.  The NI SystemLink Python SDK is installed under `C:\Program Files\National Instruments\Shared\Skyline\Python` and contains the `systemlink.clients.nitestmonitor` package imported by this example.
