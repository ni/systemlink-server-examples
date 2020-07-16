"""
SystemLink Test Monitor results example

This is an example of uploading test results to the SystemLink Test Monitor service.
It simulates measuring the power output from a device and tests the measured power
to ensure it is within a specified upper and lower limit.  The power is simulated using
a the simple electrical equation P=VI (power=voltage*current).  In this example, a random
amount of current loss and voltage loss are induced to simulate a non-ideal device.

A top level result is created containing metadata about the overall test.

The example sweeps across a range of input currents and voltages and takes measurements
for each combination and stores a single measurement within each test step.  The test
steps are associated with the test result, and in some cases, as child relationships
to other test steps.  Each step is uploaded to the SystemLink server as it is generated.
At the end, the step status is evaluated to set the status of the parent step and
ultimately sets the status of the top-level test result.
"""

import uuid
import random

from systemlink.clients.nitestmonitor import ResultsApi
from systemlink.clients.nitestmonitor import StepsApi
from systemlink.clients.nitestmonitor.models.create_test_results_request import CreateTestResultsRequest
from systemlink.clients.nitestmonitor.models.update_test_results_request import UpdateTestResultsRequest
from systemlink.clients.nitestmonitor.models.test_step_create_or_update_request_object import \
    TestStepCreateOrUpdateRequestObject
from systemlink.clients.nitestmonitor.models.test_result_request_object import TestResultRequestObject
from systemlink.clients.nitestmonitor.models.test_step_request_object import TestStepRequestObject
from systemlink.clients.nitestmonitor.models.status_object import StatusObject
from systemlink.clients.nitestmonitor.models.named_value_object import NamedValueObject


def measure_power(current: float, voltage: float = 0) -> object:
    """
    Simulates taking an electrical power measurement.
    This introduces some random current and voltage loss.
    :param current: The electrical current value.
    :param voltage: The electrical voltage value.
    :return: A tuple containing the electrical power measurements and the input and output lists.
    """
    current_loss = 1 - random.uniform(0, 1) * 0.25
    voltage_loss = 1 - random.uniform(0, 1) * 0.25
    power = current * current_loss * voltage * voltage_loss

    # Record electrical current and voltage as inputs.
    inputs = [
        NamedValueObject(name="current", value=current),
        NamedValueObject(name="voltage", value=voltage)
    ]

    # Record electrical power as an output.
    outputs = [
        NamedValueObject(name="power", value=power)
    ]

    return power, inputs, outputs


def build_power_measurement_params(
        power: float,
        low_limit: float,
        high_limit: float,
        status: object) -> object:
    """
    Builds a Test Monitor measurement parameter object for the power test.
    :param power: The electrical power measurement.
    :param low_limit: The value of the low limit for the test.
    :param high_limit: The value of the high limit for the test.
    :param status: The measurement's pass/fail status.
    :return: A list of test measurement parameters.
    """
    parameter = {
        "name": "Power Test",
        "status": str(status.status_type),
        "measurement": str(power),
        "units": "Watts",
        "nominalValue": None,
        "lowLimit": str(low_limit),
        "highLimit": str(high_limit),
        "comparisonType": "GELE"
    }

    parameters = {"text": "", "parameters": [parameter]}
    return parameters


def generate_step_data(
        name,
        step_type,
        inputs=None,
        outputs=None,
        parameters=None,
        status=None):
    """
    Creates a <see cref="StepData"/> object and
    populates it to match the TestStand data model.
    :param name: The test step's name.
    :param step_type: The test step's type.
    :param inputs: The test step's input values.
    :param outputs: The test step's output values.
    :param parameters: The measurement parameters.
    :param status:
    :return: The step data used to create a test step.
    """
    step_status = status if status is not None else StatusObject(status_type='RUNNING')

    step_data = TestStepRequestObject(
        step_id=None,
        parent_id=None,
        result_id=None,
        children=None,
        data=parameters,
        data_model="TestStand",
        name=name,
        started_at=None,
        status=step_status,
        step_type=step_type,
        total_time_in_seconds=random.uniform(0, 1) * 10,
        inputs=inputs,
        outputs=outputs)

    return step_data


def main():
    # Initialize SystemLink APIs
    results_api = ResultsApi()
    steps_api = StepsApi()

    # Set test limits
    low_limit = 0
    high_limit = 70

    test_result = TestResultRequestObject(
        program_name="Power Test",
        status=StatusObject(status_type='RUNNING'),
        system_id=None,
        host_name=None,
        properties=None,
        keywords=None,
        serial_number=str(uuid.uuid4()),
        operator="John Smith",
        part_number="NI-ABC-123-PWR",
        file_ids=None,
        started_at=None,
        total_time_in_seconds=0.0)

    create_results_request = CreateTestResultsRequest(results=[test_result])
    response = await results_api.create_results_v2(create_results_request)
    test_result = response.results[0]

    """
    Simulate a sweep across a range of electrical current and voltage.
    For each value, calculate the electrical power (P=IV).
    """
    for current in range(0, 10):
        # Generate a parent step to represent a sweep of voltages at a given current.
        voltage_sweep_step_data = generate_step_data("Voltage Sweep", "SequenceCall")
        voltage_sweep_step_data.result_id = test_result.id
        # Create the step on the SystemLink server.
        create_steps_request = TestStepCreateOrUpdateRequestObject(
            steps=[voltage_sweep_step_data],
            update_result_total_time=True)
        response = await steps_api.create_steps_v2(create_steps_request)
        voltage_sweep_step = response.steps[0]

        for voltage in range(0, 10):
            # Simulate obtaining a power measurement.
            power, inputs, outputs = measure_power(current, voltage)

            # Test the power measurement.
            status = StatusObject(status_type='FAILED') if (power < low_limit or power > high_limit) else StatusObject(
                status_type='PASSED')
            test_parameters = build_power_measurement_params(power, low_limit, high_limit, status)

            # Generate a child step to represent the power output measurement.
            measure_power_output_step_data = generate_step_data(
                "Measure Power Output",
                "NumericLimit",
                inputs,
                outputs,
                test_parameters,
                status)
            # Create the step on the SystemLink server.
            measure_power_output_step_data.parent_id = voltage_sweep_step.step_id
            measure_power_output_step_data.result_id = test_result.id
            create_steps_request = TestStepCreateOrUpdateRequestObject(
                steps=[measure_power_output_step_data],
                update_result_total_time=True)
            response = await steps_api.create_steps_v2(create_steps_request)
            measure_power_output_step = response.steps[0]

            # If a test in the sweep fails, the entire sweep failed.  Mark the parent step accordingly.
            if status.status_type == 'FAILED':
                voltage_sweep_step.status = StatusObject(status_type='FAILED')
                # Update the parent test step's status on the SystemLink server.
                update_steps_request = TestStepCreateOrUpdateRequestObject(
                    steps=[voltage_sweep_step],
                    update_result_total_time=True)
                response = await steps_api.update_steps_v2(update_steps_request)
                voltage_sweep_step = response.steps[0]

        # If none of the child steps failed, mark the step as passed.
        if voltage_sweep_step.status.status_type == 'RUNNING':
            voltage_sweep_step.status = StatusObject(status_type='PASSED')
            # Update the test step's status on the SystemLink server.
            update_steps_request = TestStepCreateOrUpdateRequestObject(
                steps=[voltage_sweep_step],
                update_result_total_time=True)
            response = await steps_api.update_steps_v2(update_steps_request)
            voltage_sweep_step = response.steps[0]

    # Update the top-level test result's status based on the most severe child step's status.
    update_result_request = UpdateTestResultsRequest(
        results=[test_result],
        determine_status_from_steps=True)
    response = await results_api.update_results_v2(update_result_request)
    test_result = response.results[0]


if __name__ == "__main__":
    main()
