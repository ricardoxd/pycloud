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
__author__ = 'Keegan'

import logging
import time

from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import CloudletPairingPage
from pycloud.manager.lib.pages import CloudletDiscoveryPage
from pycloud.pycloud.ska.bluetooth_ska_device import BluetoothSKADevice
from pycloud.pycloud.ska.adb_ska_device import ADBSKADevice
from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.pycloud.model.deployment import Deployment

from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import ajaxutils

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Pairing page.
################################################################################################################
class CloudletPairingController(BaseController):

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_pair_display()

    ############################################################################################################
    # Displays the connection to cloudlet page
    ############################################################################################################
    def GET_pair_display(self):
        page = CloudletPairingPage()

        # Generate secret to display
        page.secret = "18Y90A" #secret should be alphanumeric and 6 symbols long

        return page.render()

    ############################################################################################################
    # Does the work after data is entered
    ############################################################################################################
    def POST_pair_display(self):

        # Generate secret to display
        secret = request.params.get('secret', None)
        ssid = request.params.get('ssid', None)
        psk = request.params.get('psk', None)

        time.sleep(5)
        if ssid is not None and psk is not None:
            print "The secret = %s" % secret
            print "The ssid = %s" % ssid
            print "The psk = %s" % psk

        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    # Displays the discover page for cloudlet pairing.
    ############################################################################################################
    def GET_discover_display(self):
        page = CloudletDiscoveryPage()

        # Generate ssid and random psk here
        page.ssid = "thunder-5A34C9" #ssid should be "<cloudlet machine name>-<alphanumeric and 6 symbols long>"
        page.psk = "12AE34" #psk should be alphanumeric and 6 symbols long

        return page.render()

    ############################################################################################################
    # Does the wrk after data is entered
    ############################################################################################################
    def POST_discover_display(self):

        # Generate secret to display
        secret = request.params.get('secret', None)
        ssid = request.params.get('ssid', None)
        psk = request.params.get('psk', None)

        time.sleep(5)
        if ssid is not None and psk is not None:
            print "The secret = %s" % secret
            print "The ssid = %s" % ssid
            print "The psk = %s" % psk

        return h.redirect_to(controller='devices', action='list')

