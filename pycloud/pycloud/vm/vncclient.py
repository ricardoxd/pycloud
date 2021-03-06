# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

#!/usr/bin/env python
#       

# Used to start external processes.
import subprocess
import distutils.spawn

################################################################################################################
#
################################################################################################################
class VNCClient(object):   
    # Command used to connect to VNC tool, as well as default port.
    VNC_EXECUTABLE = 'gvncviewer'
    VNC_CONN_ARG = "localhost:%d"
    VNC_DEFAULT_PORT = 5900

    ################################################################################################################
    # Starts a VNC connection, and waits till the user closes the VNC window. 
    # Returns true if everything went ok, or false if there was a problem creating the VNC connection or if it
    # was interrupted.
    ################################################################################################################        
    def connectAndWait(self, vncPort, wait=True):
        # Starts VNC GUI in a separate process.
        try:
            vncCommandArguments = self.__getVncCommand(vncPort)
            vncPipe = subprocess.PIPE        
            vncProcess = subprocess.Popen(vncCommandArguments, shell=True, stdin=vncPipe, stdout=vncPipe, stderr=vncPipe)
        except Exception as e:
            print "Error creating VNC process: " + e.message
            return False
        
        if(wait):
            # Wait until the VNC window is closed.
            try:            
                vncProcess.wait()
            except KeyboardInterrupt:
                # If the user interrupts the process when VNC is open, we abort by destroying the VM.
                print "[INFO] Keyboard interrupt while waiting for VNC to be closed."
                return False
        
        return True        
        
    ################################################################################################################
    # Returns the VNC command to use to connect to the GUI. Only supports gvncviewer for now.
    ################################################################################################################          
    def __getVncCommand(self, vncPort):
        # First check if gvncviewer is available.
        exe_path = distutils.spawn.find_executable(self.VNC_EXECUTABLE)
        if not exe_path:
            raise Exception('Required VNC viewer "{}" was not found on the system.'.format(self.VNC_EXECUTABLE))

        # We get the display number for gvncviewer.
        displayNumber = 0
        try:
            # GVNCviewer uses not port, but display number, starting at 0. We have to substract the port the VM is
            # using from the default port to get this relative display number.
            displayNumber = int(vncPort) - self.VNC_DEFAULT_PORT
        except AttributeError as e:
            print "Warning, Possible VNC port error:%s\n" % str(e)
        
        # Now we create the command itself.
        hostArgument = self.VNC_CONN_ARG % displayNumber
        vncFullCommand = self.VNC_EXECUTABLE + ' ' + hostArgument
        #print self.VNC_EXECUTABLE + ' ' + hostArgument
            
        return vncFullCommand
