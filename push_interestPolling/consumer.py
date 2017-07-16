import sys
import time
import argparse
import traceback

from pyndn import Interest
from pyndn import Name
from pyndn import Face


class Consumer(object):
    '''Sends Interest, listens for data'''

    def __init__(self, pipeline, count):
        self.prefix = '/umobile/polling'
        self.pipeline = pipeline
        self.count = count
        self.nextSegment = 0
        self.outstanding = dict()
        self.isDone = False

        self.face = Face("127.0.0.1")

    def run(self):
        try:
            while self.nextSegment < self.pipeline:
                self._sendNextInterest(self.prefix)
                self.nextSegment += 1

            while not self.isDone:
                self.face.processEvents()
                time.sleep(0.01)

        except RuntimeError as e:
            print "ERROR: %s" % e



    def _onData(self, interest, data):
        payload = data.getContent()
        name = data.getName()

        print "Received data: %s\n" % payload.toRawStr()
        del self.outstanding[name.toUri()]

        if self.count == self.nextSegment or data.getMetaInfo().getFinalBlockID() == data.getName()[-1]:
            self.isDone = True
        else:
            self._sendNextInterest(self.prefix)
            self.nextSegment += 1


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


    def _onTimeout(self, interest):
        name = interest.getName()
        uri = name.toUri()

        print "TIMEOUT #%d: segment #%s" % (self.outstanding[uri], name[-1].toNumber())
        self.outstanding[uri] += 1

        if self.outstanding[uri] <= 3:
            self._sendNextInterestWithSegment(name)
        else:
            self.isDone = True



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse command line args for ndn consumer')

    parser.add_argument("-p", "--pipe",required=False, help='number of Interests to pipeline, default = 1', nargs= '?', const=1, type=int, default=1)
    parser.add_argument("-c", "--count", required=False, help='number of (unique) Interests to send before exiting, default = repeat until final block', nargs='?', const=1,  type=int, default=None)

    arguments = parser.parse_args()

    try:
        pipeline = arguments.pipe
        count = arguments.count

        if count is not None and count < pipeline:
            print "Number of Interests to send must be >= pipeline size"
            sys.exit(1)

        Consumer(pipeline, count).run()

    except:
        traceback.print_exc(file=sys.stdout)
        print "Error parsing command line arguments"
        sys.exit(1)