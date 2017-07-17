"""
title           : consumer.py
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
from multiprocessing import Process
import time


from pyndn import Interest
from threading import Timer, Thread, Event


class Consumer(object):
    def __init__(self):

        self.outstanding = dict()
        self.isDone = False
        self.keyChain = KeyChain()
        self.face = Face("127.0.0.1")
        self.namePrefix = '/umobile/polling/push'
        self.polling_interval = 5
        self.nextSegment = 0

    def run(self):

        try:

             ## Send Polling Interest message every 5 s
             p1 = Process(target=self.send_PollingInterest, args=(self.polling_interval,))
             p1.start()

             while not self.isDone:
                 self.face.processEvents()
                 time.sleep(0.01)


        except RuntimeError as e:
            print "ERROR: %s" % e


    def run_eventloop(self, name):
        while not self.isDone:
            self.face.processEvents()
            time.sleep(0.01)


    def send_PollingInterest(self, interval):
        while not self.isDone:
            self._sendNextInterest(Name(self.namePrefix))
            self.nextSegment += 1
            time.sleep(interval)

    def _sendNextInterest(self, name):
        self._sendNextInterestWithSegment(Name(name).appendSegment(self.nextSegment))

    def _sendNextInterestWithSegment(self, name):
        interest = Interest(name)
        uri = name.toUri()

        interest.setInterestLifetimeMilliseconds(4000)
        interest.setMustBeFresh(True)

        if name.toUri() not in self.outstanding:
            self.outstanding[name.toUri()] = 1

        self.face.expressInterest(interest, self._onData, None)
        print "Sent Interest for %s" % uri

    def _onData(self, interest, data):
        payload = data.getContent()
        dataName = data.getName()
        dataName_size = dataName.size()

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
