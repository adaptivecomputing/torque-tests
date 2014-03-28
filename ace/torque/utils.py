# NOTE: make sure the _username is the non-root username of the machine this test is running on.
# In the case of vapor instances, the non-root username will be "adaptive".
import time
from nose.tools import ok_
import sys
from ace.system.utils import *

_username = "adaptive"  # default value

def shutdown_moab_if_running():
    # Shutdown moab if it is running
    try:
        os.system('mschedctl -k > /dev/null 2>&1')
    except:
        pass 

def clean_all_jobs():
    issue_cmd(["qdel", "all"])

def is_job_in_qstat_list( target_job_id, ignore_job_status_column ):  # if True, ignore the Job Status column (4th column) in the Qstat output
    ret_val = False

    output,err = issue_cmd( "qstat" )

    linenum = 0
    for line in output.split('\n'):
        #print "line: ", linenum, "  ", line
        if line and linenum > 1:
            parts = line.split()
            #print "line: ", linenum, "  ", parts
            #print "parts[4]=>>", parts[4], "<<"
            job_id_parts = parts[0].split(".")
            #print "job_id_parts= ", job_id_parts
            job_id = job_id_parts[0]
            #print "is_job_in_qstat_list--job_id= ", job_id
            #print "is_job_in_qstat_list--target_job_id: ", target_job_id
            if job_id == target_job_id:
                #print "job_id ", job_id, "  was found in list"
                if not ignore_job_status_column:
                    # NOTE: Job status column usually has the following values:
                    # Q - means job is queued
                    # R - means job is running
                    # C - means job is complete
                    # E - means job is exiting
                    if parts[4] == "C" or parts[4] == "E":  # see if job is already completed -- if so, indicate "it's been removed"
                        break
                    else:
                        ret_val = True
                else:
                    ret_val = True

        linenum += 1

    return ret_val,output

def check_pbsnodes_result():
    ret_val = False
    node_names  = []

    output,err = issue_cmd( "pbsnodes" )
    #print "output from pbsnodes: ",output
    linenum = 0
    for line in output.split('\n'):
        #print "pbsnodes line: ", line
        if linenum == 0:
            node_names.append(line)  # add to node_names list
        parts = line.split()
        #print "line: ", parts
        #print "parts[0]= ", parts[0]
        if len(parts) == 0:  # if empty, skip it
            continue
        label = parts[0]

        if label == "state":
            # line should be: "state = free"
            value = parts[2]
            if value == "free":
                ret_val = True
            break

        linenum += 1

    return ret_val,node_names,err


def wait_for_process_to_start( process_name ):
    process_started = False
    iteration = 0
    for num in range(1,15):
        time.sleep(2)
        pid,err = get_pid ( process_name )  # make sure process was started
        if pid:
            print process_name, " was started, iteration: ", iteration
            process_started = True
            break
        else:
            print "  Couldn't start process: ", process_name, ", reason: ", err
            iteration += 1

    ok_( process_started, msg="ERROR: process: %s was not started" % process_name)

def wait_for_item_removed( function_name, job_id ):
    # make sure job has been removed from qstat list
    found_in_list = True
    iteration = 0
    output = ""
    # now delay a few seconds to let the item disappear..
    for num in range(1,120):  # loop for  120(*2) secs
        time.sleep(2)
        result,output = is_job_in_qstat_list( job_id, False )
        if not result:
            found_in_list = False
            break
        else :
            sys.stdout.write( "\r    waiting for job to be completed...  %d secs ... " % (iteration * 2) )
            sys.stdout.flush()
            iteration += 1

    ok_( not found_in_list, msg="ERROR: job %s is found in qstat list and shouldn't be, qstat results: %s" % (job_id, output))

def wait_for_item_present( function_name, job_id ):
    # make sure job is found qstat list
    found_in_list = False
    iteration = 0
    output = ""
    # now delay a few seconds to let the item appear..
    for num in range(1,120):
        time.sleep(2)
        result,output = is_job_in_qstat_list( job_id, True )
        if result:
            found_in_list = True
            break
        else :
            sys.stdout.write( "\r    waiting for job to be found in qstat list...  %d secs ... " % (iteration * 2) )
            sys.stdout.flush()
            iteration += 1

    ok_( found_in_list, msg="ERROR: job %s is NOT found in qstat list and should be, qstat results: %s" % (job_id, output))


def do_is_torque_running( ):
    sys.stdout.write("  Making sure trqauthd, pbs_server, and pbs_mom services are running... ")
    # check to see if trqauthd, pbs_server, pbs_mom are already running -- if not, start them
    pid,err = get_pid ("trqauthd")
    ok_( pid, msg="ERROR: trqauthd is not currently running")

    pid,err = get_pid ("pbs_server")
    ok_( pid, msg="ERROR: pbs_server is not currently running")

    pid,err = get_pid ("pbs_mom")
    ok_( pid, msg="ERROR: pbs_mom is not currently running")

    sys.stdout.write("OK")

def do_get_pbsnodes_result( ):
    sys.stdout.write("\n  Inspecting pbsnodes contents... ")

    result,node_names,err = check_pbsnodes_result( )
    ok_( result, msg="ERROR: pbsnodes result, node: %s, state is not free, pbsnodes output:\n%s" % (node_names[0], err))
    sys.stdout.write("OK")

