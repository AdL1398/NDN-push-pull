"""
title           : producer.py
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
import time
import traceback
import os
from pyndn import Interest
from pyndn import Data
from pyndn import Name
from pyndn import Face
from pyndn.security import KeyChain
from enumerate_publisher import EnumeratePublisher

class Producer(object):
    def __init__(self):

        Prefix = '/umobile/push_PulblishData/pull'
        self.configPrefix = Name(Prefix)
        self.outstanding = dict()
        self.isDone = False
        self.keyChain = KeyChain()
        self.face = Face("127.0.0.1")
        self.Prefix_publish = '/umobile/push_PulblishData/publish'
        self.Datamessage_size = 8000 # Data message size ~4kB

    def run(self):
        try:

            self.face.setCommandSigningInfo(self.keyChain, \
                                            self.keyChain.getDefaultCertificateName())
            self.face.registerPrefix(self.configPrefix, self.onInterest_Pull, self.onRegisterFailed)
            print "Registering listening prefix : " + self.configPrefix.toUri()

            self._sendInterest_Publish(Name(self.Prefix_publish))

            while not self.isDone:
                self.face.processEvents()
                time.sleep(0.01)

        except RuntimeError as e:
            print "ERROR: %s" % e

    def _sendInterest_Publish(self, name):
        interest = Interest(name)
        uri = name.toUri()

        interest.setInterestLifetimeMilliseconds(4000)
        interest.setMustBeFresh(True)

        if uri not in self.outstanding:
            self.outstanding[uri] = 1

        self.face.expressInterest(interest, None, None)
        print "Sent Interest for %s" % uri


    def onInterest_Pull(self, prefix, interest, face, interestFilterId, filter):

        script_path = os.path.abspath(__file__)  # i.e. /path/to/dir/foobar.py
        script_dir = os.path.split(script_path)[0]  # i.e. /path/to/dir/
        filename= 'testfile_original.docx'
        abs_file_path = os.path.join(script_dir, filename)
        freshness = 10000  # milli second, content will be deleted from the cache after freshness period
        self.sendingFile(abs_file_path, interest, face, freshness)


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

    def sendingFile(self, file_path, interest, face, freshness):
        print "Sending File Function"
        interestName = interest.getName()
        interestNameSize = interestName.size()

        try:
            SegmentNum = (interestName.get(interestNameSize - 1)).toSegment()
            dataName = interestName.getSubName(0, interestNameSize - 1)

        # If no segment number is included in the INTEREST, set the segment number as 0 and set the file name to configuration script to be sent
        except RuntimeError as e:
            SegmentNum = 0
            dataName = interestName
        # Put file to the Data message
        try:
            # due to overhead of NDN name and other header values; NDN header overhead + Data packet content = < maxNdnPacketSize
            # So Here segment size is hard coded to 5000 KB.
            # Class Enumerate publisher is used to split large files into segments and get a required segment ( segment numbers started from 0)
            dataSegment, last_segment_num = EnumeratePublisher(file_path, self.Datamessage_size, SegmentNum).getFileSegment()
            # create the DATA name appending the segment number
            dataName = dataName.appendSegment(SegmentNum)
            data = Data(dataName)
            data.setContent(dataSegment)

            # set the final block ID to the last segment number
            last_segment = (Name.Component()).fromNumber(last_segment_num)
            data.getMetaInfo().setFinalBlockId(last_segment)
            #hourMilliseconds = 600 * 1000
            data.getMetaInfo().setFreshnessPeriod(freshness)

            # currently Data is signed from the Default Identitiy certificate
            self.keyChain.sign(data, self.keyChain.getDefaultCertificateName())
            # Sending Data message
            face.send(data.wireEncode().toBuffer())
            print "Replied to Interest name: %s" % interestName.toUri()
            print "Replied with Data name: %s" % dataName.toUri()

        except ValueError as err:
            print "ERROR: %s" % err


if __name__ == '__main__':

    try:

        Producer().run()

    except:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)



