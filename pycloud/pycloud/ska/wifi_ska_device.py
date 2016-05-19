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
__author__ = 'Dan'

import subprocess
import os
import json
import socket

from ska_device_interface import ISKADevice
from pycloud.pycloud.ska import ska_constants

# Size of a chunk when transmitting through TCP .
CHUNK_SIZE = 4096

######################################################################################################################
# Checks that there is an enabled WiFi device, and returns its address.
######################################################################################################################
def get_adapter_address():
    internal_address = None

    cmd = subprocess.Popen('./start_ap.sh', shell=True, stdout=None)

    cmd = subprocess.Popen('iw dev', shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if "Interface" in line:
            internal_address = line.split(' ')[1]

    if internal_address is not None:
        print "WiFi adapter with address {} found".format(internal_address)
    else:
        print "WiFi adapter not found."

    return internal_address

######################################################################################################################
# Connects to a device given the device info dict, and returns a socket.
######################################################################################################################
def connect_to_device(host, port, name):
    print("Connecting to \"%s\" on %s" % (name, host))

    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((host, port))

    print("Connected to \"%s\" on %s" % (name, host))

    return new_socket

######################################################################################################################
#
######################################################################################################################
def comm_test(device_socket):
    print('type: ')
    while 1:
        text = raw_input()
        if text == "quit":
            break
        if text == "get_id":
            print('Getting id...')
        device_socket.send(text)

        # Wait for reply, it should be small enough to fit in one chunk.
        reply = device_socket.recv(CHUNK_SIZE)
        print 'Id: ' + str(reply)

######################################################################################################################
#
######################################################################################################################
class WiFiSKADevice(ISKADevice):

    device_socket = None
    device_info = None

    ####################################################################################################################
    # Creates a device using the provided device info dict.
    ####################################################################################################################
    def __init__(self, device):
        self.device_info = device

    ####################################################################################################################
    # Returns a name for the device.
    ####################################################################################################################
    def get_name(self):
        return self.device_info['host']

    ####################################################################################################################
    # The port.
    ####################################################################################################################
    def get_port(self):
            return self.device_info['port']

    ####################################################################################################################
    # The friendly name.
    ####################################################################################################################
    def get_friendly_name(self):
            return self.device_info['name']

    ####################################################################################################################
    #
    ####################################################################################################################
    @staticmethod
    def initialize(root_folder):
        # Nothing to be done.
        pass

    ####################################################################################################################
    #
    ####################################################################################################################
    @staticmethod
    def bootstrap():
        # Nothing to be done.
        pass

    ####################################################################################################################
    # Returns a list of devices available.
    ####################################################################################################################
    @staticmethod
    def list_devices():
        # Check that there is an adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            raise Exception("WiFi adapter not available.")

        # Find a device that has the service we want to use.
        # TODO: not implemented
        devices = []

        ska_devices = []
        for device in devices:
            ska_devices.append(WiFiSKADevice(device))

        return ska_devices

    ####################################################################################################################
    # Makes a TCP connection to this device.
    ####################################################################################################################
    def connect(self):
        # Check that there is an adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            raise Exception("WiFi adapter not available.")
        # Connect to the device.
        self.device_socket = connect_to_device(self.device_info['host'], self.device_info['port'], self.device_info['name'])
        if self.device_socket is None:
            return False
        else:
            return True

    ####################################################################################################################
    # Closes the TCP socket.
    ####################################################################################################################
    def disconnect(self):
        if self.device_socket is not None:
            self.device_socket.close()

    ####################################################################################################################
    #
    ####################################################################################################################
    def get_data(self, data):
        result = self.__send_command('send_data', data)
        return self.__parse_result(result)

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_data(self, data):
        result = self.__send_command('receive_data', data)
        return self.__parse_result(result)

    ####################################################################################################################
    # Sends a given file, ensuring the other side is ready to store it.
    ####################################################################################################################
    def send_file(self, file_path, file_id):
        result = self.__send_command('receive_file', {'file_id': file_id})
        if result == 'ack':
            # First send the file size in bytes.
            file_size = os.path.getsize(file_path)
            ack = self.__send_string(str(file_size))
            if ack == 'ack':
                # Open and send the file in chunks.
                print 'Sending file.'
                file_to_send = open(file_path, 'rb')

                # Send until there is no more data in the file.
                while True:
                    data_chunk = file_to_send.read(CHUNK_SIZE)
                    if not data_chunk:
                        break

                    sent = self.device_socket.send(data_chunk)
                    if sent < len(data_chunk):
                        print 'Error sending data chunk.'

                print 'Finished sending file. Waiting for result.'

                # Wait for final result.
                reply = self.device_socket.recv(CHUNK_SIZE)
                print 'Reply: ' + reply

                # Check result.
                return self.__parse_result(reply)

    ####################################################################################################################
    # Sends a command.
    ####################################################################################################################
    def __send_command(self, command, data):
        # Prepare command.
        message = dict(data)
        message['wifi_command'] = command
        message['cloudlet_name'] = socket.gethostname()
        message_string = json.dumps(message)

        # Send command.
        result = self.__send_string(message_string)
        return result

    ####################################################################################################################
    # Checks the success of a result.
    ####################################################################################################################
    def __parse_result(self, result):
        # Check error and log it.
        json_data = json.loads(result)
        if json_data[ska_constants.RESULT_KEY] != ska_constants.SUCCESS:
            error_messge = 'Error processing command on device: ' + json_data[ska_constants.ERROR_MSG_KEY]
            raise Exception(error_messge)

        return json.loads(result)

    ####################################################################################################################
    # Sends a short string.
    ####################################################################################################################
    def __send_string(self, data_string):
        if self.device_socket is None:
            raise Exception("Not connected to a device.")

        print 'Sending data: ' + data_string
        self.device_socket.send(data_string)

        # Wait for reply, it should be small enough to fit in one chunk.
        reply = self.device_socket.recv(CHUNK_SIZE)
        print 'Reply: ' + reply
        return reply