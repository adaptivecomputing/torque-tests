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

@attr(owner='DMarsh')
@attr(level=1)        # options are: 1, 2
@attr(suite='hpc')    # options are: hpc, hpc-enterprise, hpc-basic
@attr(jira="AC-6461")
# Bring up pbs_server and a mom; run a few basic jobs
# Basic jobs include: interactive, nodes=/ppn= submissions, procs
# Check that walltime works
class TestBasicTorque:
    @classmethod
    def setup_class(self):
        if is_running_as_root():
            print "  Running as root; non-root username:", USERNAME
        else :
            print "  Not running as root; username:", USERNAME
        self.start_time = time.time()

    @classmethod
    def teardown_class(self):
        elapsed_time = time.time() - self.start_time
        print 'Took %s seconds to run tests' % elapsed_time


    def test_01_is_torque_running(self):
        is_torque_running( )
    
    def test_02_get_pbsnodes_result(self):
        result = ""
        node_names = []
        output = ""
        err = ""
        result,node_names,output,err = check_pbsnodes_result()

        # Loops while we don't have a good result, this ignores transient errors from torque restarting
        count = 0
        while not result and count < 5:
            time.sleep(5)
            result,node_names,output,err = check_pbsnodes_result()
            count = count + 1
        ok_( result, msg="ERROR: pbsnodes result, node: %s, state is not free, standard error: %s, standard output:\n%s" % (node_names[0], err, output))

    def test_03_submit_basic_job(self):
        # submit a simple job --  echo sleep 30 | qsub
        if is_running_as_root():
            result,err = issue_cmd_as_non_root_user('qsub', "sleep 10")
        else:
            result,err = issue_cmd('qsub', "sleep 10")

        job_id_parts = result.split(".")
        job_id = job_id_parts[0]
        print "created job %s..." % job_id
        # make sure job in shown in qstat output
        #wait_for_item_present( "submit_basic_job", job_id )
        time.sleep(2)
        result, err = is_job_in_qstat_list( job_id, True )
        ok_( result, msg="ERROR: job %s is NOT found in qstat list and should be, qstat results:\n%s" % (job_id, err))

        sys.stdout.write("\n  Deleting basic job... ")
        result,err = issue_cmd( ['qdel', job_id] )

        # make sure job has been removed from qstat list
        wait_for_item_removed( "submit_basic_job", job_id )
    
    def test_04_submit_job_with_walltime(self):
        err = ""
        if is_running_as_root():
            result,err = issue_cmd_as_non_root_user( 'qsub -l walltime=10,nodes=1:ppn=4', "sleep 10000" )
        else:
            result,err = issue_cmd( ['qsub','-l', 'walltime=10,nodes=1:ppn=4'], "sleep 10000" )
        job_id_parts = result.split(".")
        job_id = job_id_parts[0]
        print "created job %s..." % job_id
        wait_for_item_present( "submit_job_with_walltime", job_id )

        if not is_process_running("moab"):
            sys.stdout.write("\n  Running job with qrun, letting walltime expire the job... \n")
            result,err = issue_cmd( ['qrun',job_id] )

        # now delay for a while to let the walltime (10 secs) expire the job..
        wait_for_item_removed( "submit_job_with_walltime", job_id )

    def test_05_submit_array_job(self):
        err = ""
        if is_running_as_root():
            result,err = issue_cmd_as_non_root_user( 'qsub -t 1-10', "sleep 20" )
        else:
            result,err = issue_cmd( ['qsub','-t', '1-10'], "sleep 20" )
        job_id_parts = result.split(".")  # array jobs will have format "105[]"
        job_id = job_id_parts[0]
        print "created job array %s..." % job_id
        # make sure job appears in qstat output
        wait_for_item_present( "submit_array_job", job_id )

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
            pass
        else:
            linenum = 0
            for line in line_array:
                print "line: ", linenum, "  ", line
                linenum += 1

            ok_(False, msg='Array job %s has %d job tasks in the array, should have 10' % (job_id, line_count))


        sys.stdout.write("\n  Ensuring selected job tasks are in array job list... ")
        # make sure that items [1] and [10] are in the list
        pieces = job_id.split('[')
        jobid = pieces[0]
        target_job_id1 = jobid + "[1]"
        target_job_id10 = jobid + "[10]"
        index1 = output.find(target_job_id1);
        index10 = output.find(target_job_id10);
        ok_( index1 != -1, msg="ERROR: job_id  %s  is NOT found in qstat list and should be, qstat results:\n%s" % (target_job_id1, output))
        ok_( index10 != -1, msg="ERROR: job_id  %s  is NOT found in qstat list and should be, qstat results:\n%s" % (target_job_id10, output))

        sys.stdout.write("\n  Deleting array job... ")
        result,err = issue_cmd( ['qdel', job_id] )
        wait_for_item_removed( "submit_array_job", job_id )

