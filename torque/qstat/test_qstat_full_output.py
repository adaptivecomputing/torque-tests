import time
from nose.plugins.attrib import attr
from nose.tools import ok_
import sys
from ace.system.utils import *
from ace.torque.utils import *


@attr(jira='TRQ-2327')
@attr(owner='echan')
@attr(level='1') 
@attr(suite='hpc')
class TestQstat:
    def analyze_qstat_full_output(self, result):
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
            
        ok_(valid_lines_count >= 20, msg='Output did not have the expected number of lines.  Expected over 20, but actual was %d.  Output: %s' % (valid_lines_count, result))
        ok_(not alps or 'BATCH_PARTITION_ID=' in variable_list, msg='Expected BATCH_PARTITION_ID environment variable, but it was not found it the output.  Output: %s' % result)

    def test_01_clean_all_jobs(self):
       clean_all_jobs()
    
    def test_02_submit_job_check_output(self):
        moab_running = True # assume moab is running
        if not is_process_running("moab"):
           moab_running = False
           ok_(is_running_as_root(), msg='You either need to have Moab started or run the test as root')
    
        print "\n  Submitting sleep job of 10 seconds..."
        if is_running_as_root():
            result,err = issue_cmd_as_non_root_user('qsub', "sleep 10")
        else:
            result,err = issue_cmd('qsub', "sleep 10")
    
        ok_('can not be' not in result and 'MSG=' not in result, msg='Job submission failed (%s)' % result)
    
        parts = result.split('\n')
        ok_(parts[0], msg='Job submission failed, job ID is empty (%s)' % result)
    
        if not moab_running:
            result,err = issue_cmd(['qrun', parts[0]])
            ok_('Unknown Job Id Error' not in result, msg='Failed to run job, error message: %s' % result)
    
        # make sure job in shown in qstat output
        #wait_for_item_present( "submit_basic_job", job_id )
        time.sleep(2)
    
        # make sure job has been removed from qstat list
        wait_for_item_removed( "test_02_submit_job_check_status", parts[0] )
     
        cmd = ['qstat', '-f', parts[0]]
        result,err = issue_cmd(cmd)
    
        ok_('Unknown Job Id Error' not in result, msg='qstat on job %s failed, unknown job ID' % parts[0])
    
        ok_(result, msg='There was a problem running qstat, output: %s' % err)
    
        self.analyze_qstat_full_output(result)
