#!/usr/bin/env python3
import os
import stat
import sys
from subprocess import Popen, PIPE
import argparse

# initialize the variables
path = "/"
noofExecutables = 0
noOfFiles = 0
setuidexecs = []
capaware = []
searchSetUidFiles = False
isearchCapableFiles = False

# set requirements based on command line arguments
parser = argparse.ArgumentParser(description='flags for findpriv')
parser.add_argument('-p')
parser.add_argument('-c',action='store_true')
parser.add_argument('-s',action='store_true')
args = parser.parse_args()
if args.p != None:
    path = args.p
searchSetUidFiles  = args.s
searchCapableFiles = args.c
if len(sys.argv)==1:
    path = "/"
    searchSetUidFiles  = True
    searchCapableFiles = True

# search the file system
for root, directories, files in os.walk(path):
    for name in files:
        noOfFiles+=1
        filename = os.path.join(root, name)
        if not os.path.isfile(filename):
            continue
#        noOfFiles+=1
        status = os.stat(filename)
        if (status.st_mode & stat.S_IXUSR) or (status.st_mode & stat.S_IXGRP) or (status.st_mode & stat.S_IXOTH) :
            noofExecutables+=1
            # check for setuid
            if searchSetUidFiles:
                if (status.st_mode & stat.S_ISUID) or (status.st_mode & stat.S_ISGID):
                    setuidexecs.append(filename)

            # check for capabilites
            if searchCapableFiles:
                process = Popen(['getcap', filename], stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                details = stdout.decode('ascii')
                if details != "":
                    details = details.split(' ')
                    result = [details[0]]
                    details = details[1].split(',')
                    for x in details:
                        result.append(x.split('=')[0])
                    capaware.append(result)

# print the data
print("Scanned ",noOfFiles," files, found ",noofExecutables," executables")
if searchSetUidFiles:
    print("setuid executables: ",len(setuidexecs))
    for x in setuidexecs:
        print(x)
if searchCapableFiles:
    print("capability-aware executables: ",len(capaware))
    for x in capaware:
        print(x[0],end=' ')
        for i in range(1,len(x)):
            print(x[i],end='')
            if i < len(x)-1:
                print(',',end='')
        print("")

# The End - author: Sarath
