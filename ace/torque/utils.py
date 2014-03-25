# NOTE: make sure the _username is the non-root username of the machine this test is running on.
# In the case of vapor instances, the non-root username will be "adaptive".
import time
from nose.tools import ok_
import sys
from ace.system.utils import issueCmd, getPid

_username = "adaptive"  # default value

def clean_all_jobs():
    issueCmd(["qdel", "all"])

def isJobInQstatList( targetJobID, ignoreJobStatusColumn ):  # if True, ignore the Job Status column (4th column) in the Qstat output
    retVal = False

    output,err = issueCmd( "qstat" )

    linenum = 0
    for line in output.split('\n'):
        #print "line: ", linenum, "  ", line
        if line and linenum > 1:
            parts = line.split()
            #print "line: ", linenum, "  ", parts
            #print "parts[4]=>>", parts[4], "<<"
            jobIDparts = parts[0].split(".")
            #print "jobIDparts= ", jobIDparts
            jobID = jobIDparts[0]
            #print "isJobInQstatList--jobID= ", jobID
            #print "isJobInQstatList--targetJobID: ", targetJobID
            if jobID == targetJobID:
                #print "jobID ", jobID, "  was found in list"
                if not ignoreJobStatusColumn:
                    # NOTE: Job status column usually has the following values:
                    # Q - means job is queued
                    # R - means job is running
                    # C - means job is complete
                    # E - means job is exiting
                    if parts[4] == "C" or parts[4] == "E":  # see if job is already completed -- if so, indicate "it's been removed"
                        break
                    else:
                        retVal = True
                else:
                    retVal = True

        linenum += 1

    return retVal,output

def checkPbsnodesResult():
    retVal = False
    nodeNames  = []

    output,err = issueCmd( "pbsnodes" )
    #print "output from pbsnodes: ",output
    linenum = 0
    for line in output.split('\n'):
        #print "pbsnodes line: ", line
        if linenum == 0:
            nodeNames.append(line)  # add to nodeNames list
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
                retVal = True
            break

        linenum += 1

    return retVal,nodeNames,err


def waitForProcessToStart( processName ):
    process_started = False
    iteration = 0
    for num in range(1,15):
        time.sleep(2)
        pid,err = getPid ( processName )  # make sure process was started
        if pid:
            print processName, " was started, iteration: ", iteration
            process_started = True
            break
        else:
            print "  Couldn't start process: ", processName, ", reason: ", err
            iteration += 1

    ok_( process_started, msg="ERROR: process: %s was not started" % processName)

def waitForItemToBeRemovedFromList( functionName, jobID ):
    # make sure job has been removed from qstat list
    foundInList = True
    iteration = 0
    output = ""
    # now delay a few seconds to let the item disappear..
    for num in range(1,120):  # loop for  120(*2) secs
        time.sleep(2)
        result,output = isJobInQstatList( jobID, False )
        if not result:
            foundInList = False
            break
        else :
            sys.stdout.write( "\r    waiting for job to be completed...  %d secs ... " % (iteration * 2) )
            sys.stdout.flush()
            iteration += 1

    ok_( not foundInList, msg="ERROR: job %s is found in qstat list and shouldn't be, qstat results: %s" % (jobID, output))

def waitForItemToAppearInList( functionName, jobID ):
    # make sure job is found qstat list
    foundInList = False
    iteration = 0
    output = ""
    # now delay a few seconds to let the item appear..
    for num in range(1,120):
        time.sleep(2)
        result,output = isJobInQstatList( jobID, True )
        if result:
            foundInList = True
            break
        else :
            sys.stdout.write( "\r    waiting for job to be found in qstat list...  %d secs ... " % (iteration * 2) )
            sys.stdout.flush()
            iteration += 1

    ok_( foundInList, msg="ERROR: job %s is NOT found in qstat list and should be, qstat results: %s" % (jobID, output))


def do_is_TORQUE_running( ):
    sys.stdout.write("  Making sure trqauthd, pbs_server, and pbs_mom services are running... ")
    # check to see if trqauthd, pbs_server, pbs_mom are already running -- if not, start them
    pid,err = getPid ("trqauthd")
    ok_( pid, msg="ERROR: trqauthd is not currently running")

    pid,err = getPid ("pbs_server")
    ok_( pid, msg="ERROR: pbs_server is not currently running")

    pid,err = getPid ("pbs_mom")
    ok_( pid, msg="ERROR: pbs_mom is not currently running")

    sys.stdout.write("OK")

def do_get_pbsnodes_result( ):
    sys.stdout.write("\n  Inspecting pbsnodes contents... ")

    result,nodeNames,err = checkPbsnodesResult( )
    ok_( result, msg="ERROR: pbsnodes result, node: %s, state is not free, pbsnodes output:\n%s" % (nodeNames[0], err))
    sys.stdout.write("OK")

