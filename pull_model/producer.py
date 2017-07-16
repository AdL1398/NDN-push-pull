"""
title           : producer.py
description     : Example of pull based communicaiton model


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
import time
import argparse
import traceback

from pyndn import Interest
from pyndn import Data
from pyndn import Exclude
from pyndn import Name
from pyndn import Face
from pyndn import InterestFilter
from pyndn.security import KeyChain


class Producer(object):
    def __init__(self):

        Prefix1 = '/umobile/test'
        self.configPrefix = Name(Prefix1)
        self.outstanding = dict()
        self.isDone = False
        self.keyChain = KeyChain()

        self.face = Face("127.0.0.1")

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
        data = Data(interestName)
        data.setContent("Test Pull based model")
        hourMilliseconds = 600 * 1000
        data.getMetaInfo().setFreshnessPeriod(hourMilliseconds)
        self.keyChain.sign(data, self.keyChain.getDefaultCertificateName())
        face.send(data.wireEncode().toBuffer())
        print "Replied to Interest name: %s" % interestName.toUri()
        print "Replied with Data name: %s" % interestName.toUri()

    def _sendNextInterest(self, name):
        interest = Interest(name)
        uri = name.toUri()

        interest.setInterestLifetimeMilliseconds(4000)
        interest.setMustBeFresh(True)

        if uri not in self.outstanding:
            self.outstanding[uri] = 1

        self.face.expressInterest(interest, self._onData, self._onTimeout)
        print "Sent Interest for %s" % uri

    def _onData(self, interest, data):
        payload = data.getContent()
        dataName = data.getName()
        dataName_size = dataName.size()

        print "Received data name: ", dataName.toUri()
        print "Received data: ", payload.toRawStr()

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

        Producer().run()

    except:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)



