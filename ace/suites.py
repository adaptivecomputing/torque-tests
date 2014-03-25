#!/usr/bin/python

import os
import re
import sys, getopt
import subprocess

# default locations
defaultMoab_Path = "/opt/moab/sbin/moab"
defaultTORQUE_pbs_server_Path1 = "/usr/sbin/pbs_server"
defaultTORQUE_pbs_server_Path2 = "/usr/local/sbin/pbs_server"
defaultTORQUE_pbs_mom_Path1 = "/usr/sbin/pbs_mom"
defaultTORQUE_pbs_mom_Path2 = "/usr/local/sbin/pbs_mom"
defaultTORQUE_trqauthd_Path1 = "/usr/sbin/trqauthd"
defaultTORQUE_trqauthd_Path2 = "/usr/local/sbin/trqauthd"
defaultMWS_mws_war_Path = "/usr/share/tomcat6/webapps/mws.war"  # if this file exists, MWS is installed
defaultMAM_Path = "/opt/mam/"


# Map suites to components that must be tested with it
suite_component_mapping = {
        'hpc-enterprise': ['moab', 'mws', 'mam', 'torque'],
        'hpc-basic': ['moab', 'mws', 'torque'],
        'cloud-xcat': ['moab', 'mws'],
        'cloud-csa': ['moab', 'mws'],
    }
suites_available = suite_component_mapping.keys() + ['hpc', 'cloud', 'all']

def isInstalled(component):
    print 'Checking if %s component is installed' % component
    if component=='moab':
        return os.path.exists(defaultMoab_Path)
    elif component=='torque':
        isTORQUEpbs_server_Installed = False
        isTORQUEpbs_mom_Installed = False
        isTORQUEtrqauthd_Installed = False

        # look in both /usr/sbin/ and /usr/local/sbin/ for torque components (Aaron and Isaac both agree)
        if os.path.exists(defaultTORQUE_pbs_server_Path1) or os.path.exists(defaultTORQUE_pbs_server_Path2):
            isTORQUEpbs_server_Installed = True

        if os.path.exists(defaultTORQUE_pbs_mom_Path1) or os.path.exists(defaultTORQUE_pbs_mom_Path2):
            isTORQUEpbs_mom_Installed = True

        if os.path.exists(defaultTORQUE_trqauthd_Path1) or os.path.exists(defaultTORQUE_trqauthd_Path2):
            isTORQUEtrqauthd_Installed = True

        # now see if TORQUE is installed
        if isTORQUEpbs_server_Installed == True and isTORQUEpbs_mom_Installed == True and isTORQUEtrqauthd_Installed == True:
            if os.path.exists(defaultTORQUE_pbs_server_Path1):
                print "TORQUE installed at /usr/sbin/ (pbs_server, pbs_mom, trqauthd all exist)"
            else:
                print "TORQUE installed at /usr/local/sbin/ (pbs_server, pbs_mom, trqauthd all exist)"
            return True
        else:
            return False
    elif component=='mws':
        return os.path.exists(defaultMWS_mws_war_Path)
    elif component=='mam':
        return os.path.isdir(defaultMAM_Path)
    else:
        return False
