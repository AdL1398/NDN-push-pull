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
import threading

class Producer(object):
    def __init__(self):

        Prefix1 = '/umobile/polling/push'
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
        data.setContent("Test Push Interest Polling model")
        hourMilliseconds = 600 * 1000
        data.getMetaInfo().setFreshnessPeriod(hourMilliseconds)
        self.keyChain.sign(data, self.keyChain.getDefaultCertificateName())
        face.send(data.wireEncode().toBuffer())
        print "Replied to Interest name: %s" % interestName.toUri()
        print "Replied with Data name: %s" % interestName.toUri()


    def onRegisterFailed(self, prefix):
        print "Register failed for prefix", prefix.toUri()
        self.isDone = True


if __name__ == '__main__':

    try:

        Producer().run()

    except:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)



