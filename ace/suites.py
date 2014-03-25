#!/usr/bin/python

import os
import re
import sys, getopt
import subprocess

# Map suites to components that must be tested with it
suite_component_mapping = {
        'hpc-enterprise': ['torque'],
        'hpc-basic': ['torque'],
    }
suites_available = suite_component_mapping.keys() + ['hpc', 'all']
