#!/usr/bin/python

# Run TestServerLogs (TORQUE nose test)
# Dave Marsh 03/18/2014

import os, sys
import time
import datetime
from datetime import date
from ace.system.utils import is_running_as_root
from ace.system.utils import issue_cmd
from ace.system.utils import issue_cmd_as_non_root_user
from nose.plugins.attrib import attr
from nose.tools import ok_
import glob
from os.path import basename
from ace.config import *


server_logs_path = os.path.join(TORQUE_HOME, "server_logs")


def file_check(fname1, fname2):  # these are the only files that should exist in the directory after restarting TORQUE
    #print "check_for_files() fname1: ", fname1, "  fname2: ", fname2

    iteration = 0
    for num in range(0, 10):
        iteration += 1
        #print "iteration: %d" % iteration
        time.sleep(2)

        found_other_files = False

        filelist = glob.glob(server_logs_path+"/20*")
        for fspec in filelist:
            filename = basename(fspec)
            if filename == fname1 or filename == fname2:
                pass
            else:
                #print "filename ",filename, " NOT one of fnames passed in"
                found_other_files = True
                break

        if not found_other_files:
            break

    if found_other_files:
        print "FAILURE: file_check(): found other files besides : ", fname1, " and: ", fname2, " in: %s, iteration: %d...." % (server_logs_path, iteration)
        return False
    else:
        print "SUCCESS: file_check(): fname1: ", fname1, "  fname2: ", fname2, " were the only files found in: %s, iteration: %d" % (server_logs_path, iteration)
        return True


@attr(owner='dmarsh')
@attr(level=1)        # options are: 1, 2
@attr(jira='AC-5291')

class TestServerLogs():

    @attr(suite='all')
    def test_mom_logs(self):
        print "\n\nServer Logs Test -- STARTING...."
        # make sure dir exists
        ok_( os.path.isdir(server_logs_path) ), "ERROR: path %s is not found" % (server_logs_path)
         # now restart TORQUE
        print "Restarting TORQUE..."
        if is_process_running('pbs_server'):
          issue_cmd(['sudo', 'qterm'])
          time.sleep(3)
        output,err = issue_cmd( ["sudo","pbs_server"] )
        #print "TORQUE restarted..."

        # enter a new parameter into torque:  qmgr -c "set server log_keep_days=2"
        output,err = issue_cmd(['qmgr', '-c', 'set server log_keep_days=2'], "")
        #print "log_keep_days  output: ", output, "  err: ", err

        # cd to mom logs dir
        os.chdir(server_logs_path)   # Change current working directory

        today = date.today()
        day = datetime.timedelta(days=1)
        one_day_ago = today - day
        two_days_ago = today - (day * 2)
        three_days_ago = today - (day * 3)
        
        print "Today's date:", today.strftime("%Y%m%d")
        print "one_day_ago's date:", one_day_ago.strftime("%Y%m%d")
        print "two_days_ago's date:", two_days_ago.strftime("%Y%m%d")
        print "three_days_ago's date:", three_days_ago.strftime("%Y%m%d")

        today_fname = today.strftime("%Y%m%d")
        one_day_ago_fname = one_day_ago.strftime("%Y%m%d")
        two_days_ago_fname = two_days_ago.strftime("%Y%m%d")
        three_days_ago_fname = three_days_ago.strftime("%Y%m%d")

        # create three 0-length files
        #fo = open(today_Logfilename, "w")
        #fo.close()
        fo = open(one_day_ago_fname, "w")
        fo.close()
        fo = open(two_days_ago_fname, "w")
        fo.close()
        fo = open(three_days_ago_fname, "w")
        fo.close()

        print "Getting each file's stat info...."
        # get file's stat information
        #stinfo01 = os.stat('log01.txt')
        stinfo02 = os.stat(one_day_ago_fname)
        stinfo03 = os.stat(two_days_ago_fname)
        stinfo04 = os.stat(three_days_ago_fname)

        secs_per_day = 60 * 60 * 24
        x = 5     # make it 5 secs earlier

        print "Modifying date-time stamps for each file -- make them 1, 2, and 3 days earlier..."
        # modify date/time stamps for files - make them 1, 2, and 3 days earlier (minus 5 secs)
        #os.utime("log01.txt",(stinfo01.st_atime - secs_per_day, stinfo01.st_mtime - secs_per_day))
        os.utime(one_day_ago_fname,(stinfo02.st_atime - (secs_per_day   + x), stinfo02.st_mtime - (secs_per_day   + x)))
        os.utime(two_days_ago_fname,(stinfo03.st_atime - (secs_per_day*2 + x), stinfo03.st_mtime - (secs_per_day*2 + x)))
        os.utime(three_days_ago_fname,(stinfo04.st_atime - (secs_per_day*3 + x), stinfo04.st_mtime - (secs_per_day*3 + x)))


        print "last modified date/time of one_day_ago_fname: %s" % time.ctime(os.path.getmtime(one_day_ago_fname))
        print "last modified date/time of two_days_ago_fname: %s" % time.ctime(os.path.getmtime(two_days_ago_fname))
        print "last modified date/time of three_days_ago_fname: %s" % time.ctime(os.path.getmtime(three_days_ago_fname))

        time.sleep(5)

        # now restart TORQUE
        print "Restarting TORQUE..."
        #output,err = issue_cmd( "/usr/local/bin/qterm" )
        output,err = issue_cmd( "qterm" )
        #print "qterm output", output, "  err: ", err
        time.sleep(5)
        #output,err = issue_cmd( "/usr/local/sbin/pbs_server" )
        output,err = issue_cmd( "pbs_server" )
        #print "pbs_server output", output, "  err: ", err
        #print "TORQUE restarted..."
        print "sleeping for 5 seconds, then calling qstat"
        time.sleep(5)
        output,err = issue_cmd("qstat")
        #print "qstat output: ", output

        print "making sure only 2 log files are in the server_logs directory..."
        retstat = file_check(today_fname, one_day_ago_fname) # loop until we only see these filenames in the dir
        ok_( retstat ), "ERROR: restarting TORQUE did not remove all but 2 latest log files in:  %s" % (server_logs_path)


