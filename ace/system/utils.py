import commands
import re
import sys
import os
import pwd
import subprocess
import time
from ace.config import *
import socket


# NOTE: make sure USERNAME is the non-root username of the machine this test is running on.
# In the case of vapor instances, the non-root username will be "adaptive".
USERNAME = "adaptive"


def is_running_as_root():
    return (os.geteuid() == 0)  # if os.geteuid()==0, then is running as root

#def get_non_root_user():
#    statinfo = os.stat(os.getcwd())
#    print statinfo
#    USERNAME = pwd.getpwuid(statinfo.st_uid).pw_name
#    print "USERNAME :", USERNAME
#    return USERNAME

def get_pid( process_name ):
    pid, err = issue_cmd( ["pgrep", process_name] )
    return pid.rstrip(),err # strip off whitespace chars

def start_service( service_name ):
    output, err = issue_cmd( ["service", service_name, "start"] )
    return output


def issue_cmd( cmd, stdin = "" ):
    #print "issue_cmd: cmd: ", cmd, ",  stdin: ",stdin
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate( stdin )
    if p.returncode!=0:
        print 'Standard output: %s' % out
        print 'Standard error: %s' % err
        raise subprocess.CalledProcessError(p.returncode, str(cmd))
    return out,err

def issue_cmd_as_non_root_user( cmd, stdin = ""):
    global USERNAME
    print "switching to non-root user: ", USERNAME, "... ",
    non_root_user_args = ['su', USERNAME, '-c']
    # cmd is a string, so append to the list
    non_root_user_args.append(cmd)
    #print "non_root_user_args: ", non_root_user_args
    #print "stdin:" , stdin
    p = subprocess.Popen(non_root_user_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate( stdin )
    if p.returncode!=0:
        print 'Standard output: %s' % out
        print 'Standard error: %s' % err
        raise subprocess.CalledProcessError(p.returncode, str(cmd))
    return out,err

def is_process_running(process_name):
    pid, err = issue_cmd(["pgrep", process_name])
    pid.rstrip(),err

    if pid:
        return 1
    else:
        return 0

def get_hostname():
    return socket.gethostname()
