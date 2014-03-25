#!/usr/bin/python

# Run TestServerLogs (TORQUE nose test)
# Dave Marsh 03/18/2014

import os, sys
import time
import datetime
from datetime import date
from ace.system.utils import isRunningAsRoot
from ace.system.utils import issueCmd
from ace.system.utils import issueCmdAsNonRootUser
from nose.plugins.attrib import attr
from nose.tools import ok_
import glob
from os.path import basename
from ace.config import *


serverLogsPath = os.path.join(TORQUE_HOME, "server_logs")


def fileCheck(fname1, fname2):  # these are the only files that should exist in the directory after restarting TORQUE
    #print "checkForFiles() fname1: ", fname1, "  fname2: ", fname2

    iteration = 0
    for num in range(0, 10):
        iteration += 1
        #print "iteration: %d" % iteration
        time.sleep(2)

        foundOtherFiles = False

        filelist = glob.glob(serverLogsPath+"/20*")
        for fspec in filelist:
            filename = basename(fspec)
            if filename == fname1 or filename == fname2:
                pass
            else:
                #print "filename ",filename, " NOT one of fnames passed in"
                foundOtherFiles = True
                break

        if not foundOtherFiles:
            break

    if foundOtherFiles:
        print "FAILURE: fileCheck(): found other files besides : ", fname1, " and: ", fname2, " in: %s, iteration: %d...." % (serverLogsPath, iteration)
        return False
    else:
        print "SUCCESS: fileCheck(): fname1: ", fname1, "  fname2: ", fname2, " were the only files found in: %s, iteration: %d" % (serverLogsPath, iteration)
        return True


@attr(owner='dmarsh')
@attr(level=1)        # options are: 1, 2
@attr(jira='AC-5291')

class TestServerLogs():

    @attr(suite='all')
    def test_mom_logs(self):
        print "\n\nServer Logs Test -- STARTING...."
        # make sure dir exists
        ok_( os.path.isdir(serverLogsPath) ), "ERROR: path %s is not found" % (serverLogsPath)
         # now restart TORQUE
        print "Restarting TORQUE..."
        output,err = issueCmd( ["sudo","pbs_server"] )
        #print "TORQUE restarted..."

        # enter a new parameter into torque:  qmgr -c "set server log_keep_days=2"
        output,err = issueCmd(['qmgr', '-c', 'set server log_keep_days=2'], "")
        #print "log_keep_days  output: ", output, "  err: ", err

        # cd to mom logs dir
        os.chdir(serverLogsPath)   # Change current working directory

        today = date.today()
        day = datetime.timedelta(days=1)
        oneDayAgo = today - day
        twoDaysAgo = today - (day * 2)
        threeDaysAgo = today - (day * 3)
        
        print "Today's date:", today.strftime("%Y%m%d")
        print "oneDayAgo's date:", oneDayAgo.strftime("%Y%m%d")
        print "twoDaysAgo's date:", twoDaysAgo.strftime("%Y%m%d")
        print "threeDaysAgo's date:", threeDaysAgo.strftime("%Y%m%d")

        today_fname = today.strftime("%Y%m%d")
        oneDayAgo_fname = oneDayAgo.strftime("%Y%m%d")
        twoDaysAgo_fname = twoDaysAgo.strftime("%Y%m%d")
        threeDaysAgo_fname = threeDaysAgo.strftime("%Y%m%d")

        # create three 0-length files
        #fo = open(today_Logfilename, "w")
        #fo.close()
        fo = open(oneDayAgo_fname, "w")
        fo.close()
        fo = open(twoDaysAgo_fname, "w")
        fo.close()
        fo = open(threeDaysAgo_fname, "w")
        fo.close()

        print "Getting each file's stat info...."
        # get file's stat information
        #stinfo01 = os.stat('log01.txt')
        stinfo02 = os.stat(oneDayAgo_fname)
        stinfo03 = os.stat(twoDaysAgo_fname)
        stinfo04 = os.stat(threeDaysAgo_fname)

        secsPerDay = 60 * 60 * 24
        x = 5     # make it 5 secs earlier

        print "Modifying date-time stamps for each file -- make them 1, 2, and 3 days earlier..."
        # modify date/time stamps for files - make them 1, 2, and 3 days earlier (minus 5 secs)
        #os.utime("log01.txt",(stinfo01.st_atime - secsPerDay, stinfo01.st_mtime - secsPerDay))
        os.utime(oneDayAgo_fname,(stinfo02.st_atime - (secsPerDay   + x), stinfo02.st_mtime - (secsPerDay   + x)))
        os.utime(twoDaysAgo_fname,(stinfo03.st_atime - (secsPerDay*2 + x), stinfo03.st_mtime - (secsPerDay*2 + x)))
        os.utime(threeDaysAgo_fname,(stinfo04.st_atime - (secsPerDay*3 + x), stinfo04.st_mtime - (secsPerDay*3 + x)))


        print "last modified date/time of oneDayAgo_fname: %s" % time.ctime(os.path.getmtime(oneDayAgo_fname))
        print "last modified date/time of twoDaysAgo_fname: %s" % time.ctime(os.path.getmtime(twoDaysAgo_fname))
        print "last modified date/time of threeDaysAgo_fname: %s" % time.ctime(os.path.getmtime(threeDaysAgo_fname))

        time.sleep(5)

        # now restart TORQUE
        print "Restarting TORQUE..."
        #output,err = issueCmd( "/usr/local/bin/qterm" )
        output,err = issueCmd( "qterm" )
        #print "qterm output", output, "  err: ", err
        time.sleep(5)
        #output,err = issueCmd( "/usr/local/sbin/pbs_server" )
        output,err = issueCmd( "pbs_server" )
        #print "pbs_server output", output, "  err: ", err
        #print "TORQUE restarted..."
        print "sleeping for 5 seconds, then calling qstat"
        time.sleep(5)
        output,err = issueCmd("qstat")
        #print "qstat output: ", output

        print "making sure only 2 log files are in the server_logs directory..."
        retstat = fileCheck(today_fname, oneDayAgo_fname) # loop until we only see these filenames in the dir
        ok_( retstat ), "ERROR: restarting TORQUE did not remove all but 2 latest log files in:  %s" % (serverLogsPath)


