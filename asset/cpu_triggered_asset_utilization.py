# -*- coding: utf-8 -*-
from __future__ import absolute_import
import argparse
import getpass
import sys
import time
import winreg

with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        'SOFTWARE\\National Instruments\\Salt\\Minion\\CurrentVersion',
        0,
        winreg.KEY_READ) as hkey:
    (SALT_COMMON_PATH, _) = winreg.QueryValueEx(hkey, 'CommonAppDataPath')
    # This looks like: C:\ProgramData\National Instruments\salt\var\cache\salt\minion\extmods
    BEACON_DIR = SALT_COMMON_PATH + 'var\\cache\\salt\\minion\\extmods'

# A helper used by the system monitoring beacon is used by this script.
# It has to be acquired from the beacon installation path.
sys.path.insert(0, BEACON_DIR)

from beacons import _nisysmgmt_health
from systemlink.assetmgmtutilclient import AssetManagementUtilization

# The parsed arguments. Set in :func:`main`.
PARSED_ARGUMENTS = None
# Whether a utilization is currently in progress.
UTILIZATION_IN_PROGRESS = False
# An instance of :class:`AssetManagementUtilization` representing the current utilization, if any.
ONGOING_UTILIZATION = None


def _stop_ongoing_utilization():
    global UTILIZATION_IN_PROGRESS
    global ONGOING_UTILIZATION
    if UTILIZATION_IN_PROGRESS:
        ONGOING_UTILIZATION.close()
        ONGOING_UTILIZATION = None
        UTILIZATION_IN_PROGRESS = False


def _start_or_update_ongoing_utilization():
    global UTILIZATION_IN_PROGRESS
    global ONGOING_UTILIZATION
    assets = PARSED_ARGUMENTS.asset_names
    if assets: # checks both None and empty string
        assets = [x.strip() for x in assets.split(',')]
    if not UTILIZATION_IN_PROGRESS:
        ONGOING_UTILIZATION = AssetManagementUtilization(
            assets,
            PARSED_ARGUMENTS.utilization_category,
            PARSED_ARGUMENTS.user_name,
            PARSED_ARGUMENTS.task_name)
        UTILIZATION_IN_PROGRESS = True
    else:
        ONGOING_UTILIZATION.update()


def _mark_as_utilized_by_cpu_percentage(cpu_value):
    if cpu_value >= PARSED_ARGUMENTS.threshold:
        _start_or_update_ongoing_utilization()
    else:
        _stop_ongoing_utilization()


def _get_mean_cpu_usage():
    tag_info = {}
    _nisysmgmt_health.setup_tags(tag_info, '')
    _nisysmgmt_health.calc_cpu(tag_info)
    return tag_info['cpu_mean_perc']['value']


def _check_cpu_triggered_utilization():
    cpu_value = _get_mean_cpu_usage()
    if PARSED_ARGUMENTS.print_recorded_cpu_values:
        print("Mean CPU utilization for the past {} minutes is {}".format(PARSED_ARGUMENTS.interval, cpu_value))
    _mark_as_utilized_by_cpu_percentage(cpu_value)


def _minutes_to_seconds(minutes):
    return minutes * 60


def loop():
    '''
    This function indefinitely snapshots CPU usage and handles the ongoing utilization.
    It uses a try-finally structure to make sure that the ongoing utilization is stopped
    when the user ends the script execution.
    '''
    try:
        while True:
            _nisysmgmt_health.cpu_usage_snapshot()
            time.sleep(_minutes_to_seconds(PARSED_ARGUMENTS.interval))
            _check_cpu_triggered_utilization()
    finally:
        _stop_ongoing_utilization()


def main(arguments=None):
    global PARSED_ARGUMENTS
    logged_user_name = getpass.getuser()
    parser = argparse.ArgumentParser(description = 'CPU usage triggered asset utilization.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', nargs ='+', action = 'store')
    parser.add_argument('--threshold', '-th', type = int, default = 15, help = 'The threshold percentage that triggers the utilization start.')
    parser.add_argument('--interval', '-i', type = int, default = 5, help = 'Interval in minutes used to check the CPU usage.')
    parser.add_argument('--asset_names', '-a', default = None, help = 'The asset names that will be used in the utilization entries separated by commas.')
    parser.add_argument('--utilization_category', '-c', default = 'Test', help = 'The utilization category that will be used in the utilization entries.')
    parser.add_argument('--user_name', '-u', default = logged_user_name, help = 'The user name that will be used in the utilization entries. Defaults to the logged user.')
    parser.add_argument('--task_name', '-t', default = 'cpu_usage_triggered_utilization', help = 'The task name that will be used in the utilization entries.')
    parser.add_argument('--print_recorded_cpu_values', '-p', action = 'store_true', help = 'Prints the CPU usage once for every interval.')
    PARSED_ARGUMENTS = parser.parse_args(sys.argv if arguments is None else arguments)
    loop()


if __name__ == '__main__':
    main()