import commands
import re
import sys
import os
import pwd
import subprocess
import time

# NOTE: make sure the username is the non-root username of the machine this test is running on.
# In the case of vapor instances, the non-root username will be "adaptive".
username = "adaptive"  # default value


def isRunningAsRoot():
    return (os.geteuid() == 0)  # if os.geteuid()==0, then is running as root

#def getNonRootUser():
#    statinfo = os.stat(os.getcwd())
#    print statinfo
#    username = pwd.getpwuid(statinfo.st_uid).pw_name
#    print "username :", username
#    return username

def getPid( processName ):
    pid, err = issueCmd( ["pgrep", processName] )
    return pid.rstrip(),err # strip off whitespace chars

def startService( serviceName ):
    output, err = issueCmd( ["service", serviceName, "start"] )
    return output


def issueCmd( cmd, stdin = "" ):
    #print "issueCmd: cmd: ", cmd, ",  stdin: ",stdin
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate( stdin )
    return out,err

def issueCmdAsNonRootUser( cmd, stdin = ""):
    global username
    print "switching to non-root user: ", username, "... ",
    nonRootUserArgs = ['su', username, '-c']
    # cmd is a string, so append to the list
    nonRootUserArgs.append(cmd)
    #print "nonRootUserArgs: ", nonRootUserArgs
    #print "stdin:" , stdin
    p = subprocess.Popen(nonRootUserArgs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate( stdin )
    return out,err

def isProcessRunning(processName):
    pid, err = issueCmd(["pgrep", processName])
    pid.rstrip(),err

    if pid:
        return 1
    else:
        return 0
