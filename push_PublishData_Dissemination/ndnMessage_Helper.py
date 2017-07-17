"""
title           : ndnMessageHelper.py
description     : This module is used to extract the Data message and send the next Interest

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


import os

def extractData_message(path, fileName, data):
    payload = data.getContent()
    dataName = data.getName()
    dataName_size = dataName.size()
    print "Extracting Data message name: ", dataName.toUri()
    #print "Received data: ", payload.toRawStr()
    if not os.path.exists(path):
            os.makedirs(path)

    with open(os.path.join(path, fileName), 'ab') as temp_file:
        temp_file.write(payload.toRawStr())
        # if recieved Data is a segment of the file, then need to fetch remaning segments
        # try if segment number is existed in Data Name
    try:
        dataSegmentNum = (dataName.get(dataName_size - 1)).toSegment()
        lastSegmentNum = (data.getMetaInfo().getFinalBlockId()).toNumber()
        print "dataSegmentNum" + str(dataSegmentNum)
        print "lastSegmentNum" + str(lastSegmentNum)

        # If segment number is available and what have recieved is not the FINAL_BLOCK, then fetch the NEXT segment
        if lastSegmentNum != dataSegmentNum:
            interestName = dataName.getSubName(0, dataName_size - 1)
            interestName = interestName.appendSegment(dataSegmentNum + 1)
            return False, interestName
            #self._sendNextInterest(interestName, self.interestLifetime, 'pull')
        # If segment number is available and what have recieved is the FINAL_BLOCK, then EXECUTE the configuration script
        ### Recieve all chunks of data --> Execute it here

        elif lastSegmentNum == dataSegmentNum:
            print "Received complete Data message: %s  " %fileName
            interestName = 'complete'
            return True, interestName
        else:
            print 'Data segment failed'

    except RuntimeError as e:
            print "ERROR: %s" % e
            #self.isDone = True
