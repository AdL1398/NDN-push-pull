"""
title           : consumer.py
description     : Example of push Publish Data Dissemination model


source          :
author          : Adisorn Lertsinsrubtavee
date            : 25 June 2017
version         : 1.0
contributors    :
usage           :
notes           :
compile and run : It is a python module imported by a main python programme.
python_version  : Python 2.7.12
====================================================
"""

import sys
import argparse
import traceback
import time
import os
import subprocess

from pyndn import Name
from pyndn import Data
from pyndn import Face
from pyndn import InterestFilter
from pyndn.security import KeyChain
from pyndn import Interest


class Consumer(object):
    def __init__(self):

        self.outstanding = dict()
        self.isDone = False
        self.keyChain = KeyChain()
        self.face = Face("127.0.0.1")
        self.nameInput = '/umobile/push_PulblishData/publish'
        self.configPrefix = Name(self.nameInput)

    def run(self):

        try:

            self.face.setCommandSigningInfo(self.keyChain, \
                                            self.keyChain.getDefaultCertificateName())
            self.face.registerPrefix(self.configPrefix, self.onInterest, self.onRegisterFailed)
            print "Registering listening prefix : " + self.configPrefix.toUri()

            while not self.isDone:
                self.face.processEvents()
                time.sleep(0.01)


        except RuntimeError as e:
            print "ERROR: %s" % e


    def onInterest(self, prefix, interest, face, interestFilterId, filter):

        interestName = interest.getName()
        #data = Data(interestName)
        #data.setContent("Test Pull based model")
        #hourMilliseconds = 600 * 1000
        #data.getMetaInfo().setFreshnessPeriod(hourMilliseconds)
        #self.keyChain.sign(data, self.keyChain.getDefaultCertificateName())
        #face.send(data.wireEncode().toBuffer())
        print "Received Publish Interest message"
        name_prefix = '/umobile/push_PulblishData/pull'
        self._sendNextInterest(Name(name_prefix))


    def _sendNextInterest(self, name):
        interest = Interest(name)
        uri = name.toUri()

        interest.setInterestLifetimeMilliseconds(4000)
        interest.setMustBeFresh(True)

        if uri not in self.outstanding:
            self.outstanding[uri] = 1

        self.face.expressInterest(interest, self._onData, self._onTimeout)
        print "Sent Pull Interest for %s" % uri

    def _onData(self, interest, data):
        payload = data.getContent()
        dataName = data.getName()
        print "Received data name: ", dataName.toUri()
        print "Received data: ", payload.toRawStr()
        self.isDone = True


    def _onTimeout(self, interest):
        name = interest.getName()
        uri = name.toUri()

        print "TIMEOUT #%d: %s" % (self.outstanding[uri], uri)
        self.outstanding[uri] += 1

        if self.outstanding[uri] <= 3:
            self._sendNextInterest(name)
        else:
            self.isDone = True

    def onRegisterFailed(self, prefix):
        print "Register failed for prefix", prefix.toUri()
        self.isDone = True


if __name__ == '__main__':

    try:

        Consumer().run()

    except:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
