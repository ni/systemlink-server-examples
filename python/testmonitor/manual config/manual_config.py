"""
SystemLink Test Monitor manual config example

This is an example of uploading a test result to the SystemLink Test Monitor service
using a manual configuration.  This is helpful when accessing the SystemLink server from
a device that is not registered with the server.

This example accepts command-line arguments to configure the connection to the SystemLink server.
The connection URL can be specified to connect to a specific SystemLink server.  Optionally,
the user can specify either an API key or a username and password to connect to the server.

Once a connection is configured, a simple test result (with no child steps) is created on
the server to validate that the connection information succeeds in accessing the server.
"""

import sys
import uuid

from systemlink.clients.nitestmonitor import ApiClient, ResultsApi
from systemlink.clients.nitestmonitor.configuration import Configuration
from systemlink.clients.nitestmonitor.models.create_test_results_request import CreateTestResultsRequest
from systemlink.clients.nitestmonitor.models.test_result_request_object import TestResultRequestObject
from systemlink.clients.nitestmonitor.models.status_object import StatusObject


def main():
    # Set default values
    host = "http://localhost/nitestmonitor"
    api_key = None
    api_key_prefix = None
    username = None
    password = None

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if "--host:" in arg:
            host = arg.replace("--host:", "")
        if "--api_key:" in arg:
            api_key = arg.replace("--api_key:", "")
        if "--api_key_prefix:" in arg:
            host = arg.replace("--api_key_prefix:", "")
        if "--username:" in arg:
            username = arg.replace("--username:", "")
        if "--password:" in arg:
            password = arg.replace("--password:", "")

    # Create a configuration specifying the server credentials
    configuration = Configuration(
        host=host, api_key=api_key, api_key_prefix=api_key_prefix, username=username, password=password
    )
    http_client = ApiClient(configuration)

    # Initialize SystemLink APIs
    results_api = ResultsApi(http_client)

    test_result = TestResultRequestObject(
        program_name="Manual Config",
        status=StatusObject(status_type="PASSED"),
        system_id=None,
        host_name=None,
        properties=None,
        keywords=None,
        serial_number=str(uuid.uuid4()),
        operator="John Smith",
        part_number="NI-ABC-123-MAN-CFG",
        file_ids=None,
        started_at=None,
        total_time_in_seconds=1
    )

    create_results_request = CreateTestResultsRequest(results=[test_result])
    response = await results_api.create_results_v2(create_results_request)
    test_result = response.results[0]


if __name__ == "__main__":
    main()
