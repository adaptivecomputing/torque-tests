#!/usr/bin/python


# Run basic tests (torque --about and showq) to make sure that torque is cool
# Dave Marsh 12/17/2013


import sys
import os
import subprocess
import time
from ace.system.utils import *
from nose.plugins.attrib import attr
from nose.tools import ok_
from ace.torque.utils import *
from ace.config import *


def do_submit_basic_job( ):
    sys.stdout.write("\n  Submitting basic job... ")
    # submit a simple job --  echo sleep 30 | qsub
    if is_running_as_root():
        result,err = issue_cmd_as_non_root_user('qsub', "sleep 10")
    else:
        result,err = issue_cmd('qsub', "sleep 10")

    job_id_parts = result.split(".")
    job_id = job_id_parts[0]
    print "created job: %s..." % job_id
    # make sure job in shown in qstat output
    #wait_for_item_present( "do_submit_basic_job", job_id )
    time.sleep(2)
    result, err = is_job_in_qstat_list( job_id, True )
    ok_( result, msg="ERROR: job %s is NOT found in qstat list and should be, qstat results:\n%s" % (job_id, err))
    sys.stdout.write("OK")

    sys.stdout.write("\n  Deleting basic job... ")
    result,err = issue_cmd( ['qdel', job_id] )

    # make sure job has been removed from qstat list
    wait_for_item_removed( "do_submit_basic_job", job_id )
    sys.stdout.write("OK")


def do_submit_job_with_walltime( ):
    sys.stdout.write("\n  Submitting complex job with walltime, nodes, ppn... ")
    err = ""
    if is_running_as_root():
        result,err = issue_cmd_as_non_root_user( 'qsub -l walltime=10,nodes=1:ppn=4', "sleep 10000" )
    else:
        result,err = issue_cmd( ['qsub','-l', 'walltime=10,nodes=1:ppn=4'], "sleep 10000" )
    job_id_parts = result.split(".")
    job_id = job_id_parts[0]
    print "created job: %s..." % job_id
    wait_for_item_present( "do_submit_job_with_walltime", job_id )
    sys.stdout.write("OK")

    sys.stdout.write("\n  Running job with qrun, letting walltime expire the job... \n")
    result,err = issue_cmd( ['qrun',job_id] )
    # now delay for a while to let the walltime (10 secs) expire the job..
    wait_for_item_removed( "do_submit_job_with_walltime", job_id )
    sys.stdout.write("OK")


def do_submit_array_job( ):
    sys.stdout.write("\n  Submitting array job... ")
    err = ""
    if is_running_as_root():
        result,err = issue_cmd_as_non_root_user( 'qsub -t 1-10', "sleep 20" )
    else:
        result,err = issue_cmd( ['qsub','-t', '1-10'], "sleep 20" )
    job_id_parts = result.split(".")  # array jobs will have format "105[]"
    job_id = job_id_parts[0]
    print "created job array: %s..." % job_id
    # make sure job appears in qstat output
    wait_for_item_present( "do_submit_array_job", job_id )
    sys.stdout.write("OK")

    sys.stdout.write("\n  Ensuring there are 10 job tasks in the job array... ")
    output,err = issue_cmd( ['qstat','-t', job_id ] ) # list contents of array
    line_array = output.split('\n')

    # subtract 3 from line_count -- 2 header lines at front:
    #
    #line:  0    Job ID                    Name             User            Time Use S Queue
    #line:  1    ------------------------- ---------------- --------------- -------- - -----
    #
    # ..and acount for the empty line at the end
    line_count = len(line_array) - 3

    if line_count == 10:
        #print "array job ", job_id, " has 10 job tasks in the array"
        pass
    else:
        print "ERROR: array job ", job_id, "  has: ", line_count, " job tasks in the array; should have 10:\n",  # NOTE: the final comma in this line prevents it from making a new line
        linenum = 0
        for line in line_array:
            print "line: ", linenum, "  ", line
            linenum += 1

        assert False
    sys.stdout.write("OK")


    sys.stdout.write("\n  Ensuring selected job tasks are in array job list... ")
    # make sure that items [1] and [10] are in the list
    pieces = job_id.split('[')
    jobid = pieces[0]
    target_job_id1 = jobid + "[1]"
    target_job_id10 = jobid + "[10]"
    index1 = output.find(target_job_id1);
    index10 = output.find(target_job_id10);
    #print "job_id1: ", target_job_id1, ", index1: ", index1, ",  job_id10: ", target_job_id10, ", index10: ", index10
    ok_( index1 != -1, msg="ERROR: job_id  %s  is NOT found in qstat list and should be, qstat results:\n%s" % (target_job_id1, output))
    ok_( index10 != -1, msg="ERROR: job_id  %s  is NOT found in qstat list and should be, qstat results:\n%s" % (target_job_id10, output))
    sys.stdout.write("OK")

    sys.stdout.write("\n  Deleting array job... ")
    result,err = issue_cmd( ['qdel', job_id] )
    # now delay a few seconds to let the qdel happen..
    wait_for_item_removed( "do_submit_array_job", job_id )
    sys.stdout.write("OK")





@attr(owner='DMarsh')
@attr(level=1)        # options are: 1, 2
@attr(suite='hpc')    # options are: hpc, hpc-enterprise, hpc-basic
@attr(jira="AC-6461")
class TestBasicTorque:
    def test_basic_torque(self):
        if is_running_as_root():
            print "  Running as root; non-root username:", USERNAME
        else :
            print "  Not running as root; username:", USERNAME
    
        start_time = time.time()
        # Bring up pbs_server and a mom; run a few basic jobs
        # Basic jobs include: interactive, nodes=/ppn= submissions, procs
        # Check that walltime works
    
        do_is_torque_running( )
    
        do_get_pbsnodes_result( )

        do_submit_basic_job( )
        do_submit_job_with_walltime( )
        do_submit_array_job( )
    
        # your code
        elapsed_time = time.time() - start_time

