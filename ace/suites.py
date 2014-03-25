#!/usr/bin/python

import os
import re
import sys, getopt
import subprocess

# default locations
defaultTORQUE_pbs_server_Path1 = "/usr/sbin/pbs_server"
defaultTORQUE_pbs_server_Path2 = "/usr/local/sbin/pbs_server"
defaultTORQUE_pbs_mom_Path1 = "/usr/sbin/pbs_mom"
defaultTORQUE_pbs_mom_Path2 = "/usr/local/sbin/pbs_mom"
defaultTORQUE_trqauthd_Path1 = "/usr/sbin/trqauthd"
defaultTORQUE_trqauthd_Path2 = "/usr/local/sbin/trqauthd"

# Map suites to components that must be tested with it
suite_component_mapping = {
        'hpc-enterprise': ['torque'],
        'hpc-basic': ['torque'],
    }
suites_available = suite_component_mapping.keys() + ['hpc', 'all']
