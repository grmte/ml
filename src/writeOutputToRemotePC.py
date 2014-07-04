#============================================================[ Import Modules ]============================================================

import paramiko
import os, sys

#==========================================================[ Global Declarations ]=========================================================

gIPAddress = ""
gUserName = ""
gPassWord = ""
gSSH = None
gOutputDirectory = ""
gOutputFilename = ""

#============================================================[ Main Coding ]===============================================================

def initialize(pRemoteDirectory, pRemoteFilename, pRemotePCCredentials):
    global gIPAddress, gUserName, gPassWord, gSSH, gOutputDirectory, gOutputFilename
    
    try:
        gSSH = None
        gIPAddress = pRemotePCCredentials[0]
        gUserName = pRemotePCCredentials[1]
        gPassWord = pRemotePCCredentials[2]
        gOutputDirectory = pRemoteDirectory
        gOutputFilename = pRemoteFilename
    except Exception, e:
        print "Exception @Initialize: ", e
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def connectToRemoteHost():
    global gIPAddress, gUserName, gPassWord, gSSH
    
    try:
        gSSH = paramiko.SSHClient()
        gSSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        gSSH.connect(gIPAddress, username=gUserName, password=gPassWord , port=90)
        print "\nConnected to host ", gIPAddress
    except Exception, e:
        print "Exception @Connect: ", e
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def writeIntoRemoteFile(pStringToPrint):
    global gSSH, gOutputDirectory, gOutputFilename
    
    try:
        lCmd = 'echo -e \'' + pStringToPrint + '\' | cat >> ' + gOutputDirectory + gOutputFilename
#         print "Write: ", lCmd
        stdin, stdout, stderr = gSSH.exec_command(lCmd)
    except Exception, e:
        print "Exception @Write: ", e
        gSSH.close()
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def clear_file_from_remote_PC(pRemoteDirectory, pRemoteFilename, pRemotePCCredentials):
    global gSSH, gOutputDirectory, gOutputFilename
    initialize(pRemoteDirectory, pRemoteFilename, pRemotePCCredentials)
    connectToRemoteHost()    
    try:
        lCmd = 'echo "" >' + gOutputDirectory + gOutputFilename
#         print "Write: ", lCmd
        stdin, stdout, stderr = gSSH.exec_command(lCmd)
    except Exception, e:
        print "Exception @Remove contents: ", e
        gSSH.close()
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def main(pStringToPrint, pRemoteDirectory, pRemoteFilename, pRemotePCCredentials):
    global gSSH
    
    initialize(pRemoteDirectory, pRemoteFilename, pRemotePCCredentials)
    connectToRemoteHost()
    writeIntoRemoteFile(pStringToPrint)
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#-EOC-