#!/usr/bin/python


# Run basic tests (TORQUE --about and showq) to make sure that TORQUE is cool
# Dave Marsh 12/17/2013


import sys
import os
import subprocess
import time
from ace.system.utils import isRunningAsRoot
from ace.system.utils import issueCmd
from ace.system.utils import issueCmdAsNonRootUser
from nose.plugins.attrib import attr
from nose.tools import ok_
from ace.torque.utils import isJobInQstatList, waitForItemToBeRemovedFromList, waitForItemToAppearInList, \
    do_is_TORQUE_running, do_get_pbsnodes_result, _username


def do_submit_basic_job( ):
    sys.stdout.write("\n  Submitting basic job... ")
    # submit a simple job --  echo sleep 30 | qsub
    if isRunningAsRoot():
        result,err = issueCmdAsNonRootUser('qsub', "sleep 10")
    else:
        result,err = issueCmd('qsub', "sleep 10")

    jobIDparts = result.split(".")
    jobID = jobIDparts[0]
    print "created job: %s..." % jobID
    # make sure job in shown in qstat output
    #waitForItemToAppearInList( "do_submit_basic_job", jobID )
    time.sleep(2)
    result, err = isJobInQstatList( jobID, True )
    ok_( result, msg="ERROR: job %s is NOT found in qstat list and should be, qstat results:\n%s" % (jobID, err))
    sys.stdout.write("OK")

    sys.stdout.write("\n  Deleting basic job... ")
    result,err = issueCmd( ['qdel', jobID] )

    # make sure job has been removed from qstat list
    waitForItemToBeRemovedFromList( "do_submit_basic_job", jobID )
    sys.stdout.write("OK")


def do_submit_job_with_walltime( ):
    sys.stdout.write("\n  Submitting complex job with walltime, nodes, ppn... ")
    err = ""
    if isRunningAsRoot():
        result,err = issueCmdAsNonRootUser( 'qsub -l walltime=10,nodes=1:ppn=4', "sleep 10000" )
    else:
        result,err = issueCmd( ['qsub','-l', 'walltime=10,nodes=1:ppn=4'], "sleep 10000" )
    jobIDparts = result.split(".")
    jobID = jobIDparts[0]
    print "created job: %s..." % jobID
    waitForItemToAppearInList( "do_submit_job_with_walltime", jobID )
    sys.stdout.write("OK")

    sys.stdout.write("\n  Running job with qrun, letting walltime expire the job... \n")
    result,err = issueCmd( ['qrun',jobID] )
    # now delay for a while to let the walltime (10 secs) expire the job..
    waitForItemToBeRemovedFromList( "do_submit_job_with_walltime", jobID )
    sys.stdout.write("OK")


def do_submit_array_job( ):
    sys.stdout.write("\n  Submitting array job... ")
    err = ""
    if isRunningAsRoot():
        result,err = issueCmdAsNonRootUser( 'qsub -t 1-10', "sleep 20" )
    else:
        result,err = issueCmd( ['qsub','-t', '1-10'], "sleep 20" )
    jobIDparts = result.split(".")  # array jobs will have format "105[]"
    jobID = jobIDparts[0]
    print "created job array: %s..." % jobID
    # make sure job appears in qstat output
    waitForItemToAppearInList( "do_submit_array_job", jobID )
    sys.stdout.write("OK")

    sys.stdout.write("\n  Ensuring there are 10 job tasks in the job array... ")
    output,err = issueCmd( ['qstat','-t', jobID ] ) # list contents of array
    lineArray = output.split('\n')

    # subtract 3 from lineCount -- 2 header lines at front:
    #
    #line:  0    Job ID                    Name             User            Time Use S Queue
    #line:  1    ------------------------- ---------------- --------------- -------- - -----
    #
    # ..and acount for the empty line at the end
    lineCount = len(lineArray) - 3

    if lineCount == 10:
        #print "array job ", jobID, " has 10 job tasks in the array"
        pass
    else:
        print "ERROR: array job ", jobID, "  has: ", lineCount, " job tasks in the array; should have 10:\n",  # NOTE: the final comma in this line prevents it from making a new line
        linenum = 0
        for line in lineArray:
            print "line: ", linenum, "  ", line
            linenum += 1

        assert False
    sys.stdout.write("OK")


    sys.stdout.write("\n  Ensuring selected job tasks are in array job list... ")
    # make sure that items [1] and [10] are in the list
    pieces = jobID.split('[')
    jobid = pieces[0]
    targetjobID1 = jobid + "[1]"
    targetjobID10 = jobid + "[10]"
    index1 = output.find(targetjobID1);
    index10 = output.find(targetjobID10);
    #print "jobID1: ", targetjobID1, ", index1: ", index1, ",  jobID10: ", targetjobID10, ", index10: ", index10
    ok_( index1 != -1, msg="ERROR: jobID  %s  is NOT found in qstat list and should be, qstat results:\n%s" % (targetjobID1, output))
    ok_( index10 != -1, msg="ERROR: jobID  %s  is NOT found in qstat list and should be, qstat results:\n%s" % (targetjobID10, output))
    sys.stdout.write("OK")

    sys.stdout.write("\n  Deleting array job... ")
    result,err = issueCmd( ['qdel', jobID] )
    # now delay a few seconds to let the qdel happen..
    waitForItemToBeRemovedFromList( "do_submit_array_job", jobID )
    sys.stdout.write("OK")





@attr(owner='DMarsh')
@attr(level=1)        # options are: 1, 2
@attr(suite='hpc')    # options are: hpc, cloud, hpc-enterprise, hpc-basic, cloud-csa, cloud-xcat -- if you want both, use: @attr(suite='all') syntax
@attr(jira="AC-6461")
class TestBasicTorque:
    # Test attributes - must be defined just before the routine they apply to
    def test_basic_torque(self):
    #    _username = getNonRootUser()
        if isRunningAsRoot():
            print "  Running as root; non-root username:", _username
        else :
            print "  Not running as root; username:", _username
    
        start_time = time.time()
        # TORQUE LEVEL1 TESTS:
        # Normal Mode -- bring up pbs_server and a mom; run a few basic jobs
        # basic jobs include: interactive, nodes=/ppn= submissions, procs
        # Check that walltime works.
    
        do_is_TORQUE_running( )
    
        do_get_pbsnodes_result( )

        do_submit_basic_job( )
        do_submit_job_with_walltime( )
        do_submit_array_job( )
    
        # your code
        elapsed_time = time.time() - start_time

