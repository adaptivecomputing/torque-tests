import time
from nose.plugins.attrib import attr
import sys
from ace.system.utils import *
from ace.torque.utils import *


def analyze_qstat_full_output(result):
    lines = result.split('\n');
    alps = False
    variable_list = ""   
    valid_lines_count = 0

    for line in lines:
        if "Job_Name = " in line:
           valid_lines_count += 1
        elif "Job_Owner = " in line:
           valid_lines_count += 1
        elif "resources_used.cput = " in line:
           valid_lines_count += 1
        elif "resources_used.mem = " in line:
           valid_lines_count += 1
        elif "resources_used.vmem = " in line:
           valid_lines_count += 1
        elif "resources_used.walltime = " in line:
           valid_lines_count += 1
        elif "job_state = " in line:
           valid_lines_count += 1
        elif "queue = " in line:
           valid_lines_count += 1
        elif "server = " in line:
           valid_lines_count += 1
        elif "Checkpoint = " in line:
           valid_lines_count += 1
        elif "ctime = " in line:
           valid_lines_count += 1
        elif "Error_Path = " in line:
           valid_lines_count += 1
        elif "exec_host = " in line:
           valid_lines_count += 1
        elif "exec_port = " in line:
           valid_lines_count += 1
        elif "Hold_Types = " in line:
           valid_lines_count += 1
        elif "Join_Path = " in line:
           valid_lines_count += 1
        elif "Keep_Files = " in line:
           valid_lines_count += 1
        elif "Mail_Points = " in line:
           valid_lines_count += 1
        elif "mtime = " in line:
           valid_lines_count += 1
        elif "Output_Path = " in line:
           valid_lines_count += 1
        elif "Priority = " in line:
           valid_lines_count += 1
        elif "qtime = " in line:
           valid_lines_count += 1
        elif "Rerunable = " in line:
           valid_lines_count += 1
        elif "Resource_List.walltime = " in line:
           valid_lines_count += 1
        elif "session_id = " in line:
           valid_lines_count += 1
        elif "etime = " in line:
           valid_lines_count += 1
        elif "exit_status = " in line:
           valid_lines_count += 1
        elif "start_time = " in line:
           valid_lines_count += 1
        elif "start_count = " in line:
           valid_lines_count += 1
        elif "fault_tolerant = " in line:
           valid_lines_count += 1
        elif "comp_time = " in line:
           valid_lines_count += 1
        elif "job_radix = " in line:
           valid_lines_count += 1
        elif "total_runtime = " in line:
           valid_lines_count += 1
        elif "submit_host = " in line:
           valid_lines_count += 1
        elif "reservation_id" in line:
           alps = True
        elif "Variable_List" in line:
           variable_list = line
           valid_lines_count += 1
        
    if valid_lines_count < 20:
          sys.stdout.write("  output did not have the expected number of lines")
          print "Expected over 20, actual was ", valid_lines_count
          print result
          assert False

    if alps:
       if not "BATCH_PARTITION_ID=" in variable_list:
          print "  expected BATCH_PARTITION_ID environment variable not found"
          assert False

def submit_run_job_check_status():
    moab_running = True # assume moab is running
    if not is_process_running("moab"):
       moab_running = False
       if not is_running_as_root():
          print " You either have to have moab started or run this test as root\n"
          assert False     

    print "\n  Submitting sleep job of 10 seconds..."
    if is_running_as_root():
        result,err = issue_cmd_as_non_root_user('qsub', "sleep 10")
    else:
        result,err = issue_cmd('qsub', "sleep 10")

    if ("can not be" in result) or ("MSG=" in result) :
        print " Job Submission failed\n"
        assert False

    parts = result.split('\n')
    if not parts[0]:
        print " Job Submission failed. Job ID is empty"
        assert False

    if not moab_running:
        result,err = issue_cmd(['qrun', parts[0]])
        if "Unknown Job Id Error" in result:
            print "  Failed to run job, error message was: ", result
            assert False

    print "\n  waiting 25 seconds for job %s to complete" % (parts[0])
    time.sleep(25)
 
    cmd = ['qstat', '-f', parts[0]]
    result,err = issue_cmd(cmd)

    if "Unknown Job Id Error" in result:
        print "  qstat on job " + parts[0] + " failed\n"
        assert False

    if not result:
       print "  it appeared qstat did not get forked and executed..."
       print "  checking on err to see what went wrong..."
       print "  stderr had: " + err
       assert False

    analyze_qstat_full_output(result)

@attr(jira='TRQ-2327')
@attr(owner='echan')
@attr(level='1') 
@attr(suite='hpc')
class TestQstat:
    def test_qstat_full(self):
       clean_all_jobs()
       submit_run_job_check_status()
