#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************
# This program sends the data to kinesis
# Usage python pushToKinesis.py <file name>
# a lambda function will be triggered as a result, that will send it to AWS ML for classification
# Usage python pushToKinesis.py <csv file name with extension>

import sys,csv,json

import boto3

sys.path.append('../utils')
import aws


KINESIS_STREAM_NAME = 'mtaStream'



def main(fileName):
    # Ideally you should write code to get data from mta feed,clean it up and send to kinesis
    # Kinesis triggers a lambda function whcih will send the data to aws ML for classification
    # But for demo I am going to use the csv file given and in aws lambda we remove the label before 
    # sending it to aws ml
    
    # connect to kinesis
    kinesis = aws.getClient('kinesis','us-east-1')
    data = [] # list of dictionaries will be sent to kinesis
    with open(fileName,'rb') as f:
    	dataReader = csv.DictReader(f)
        for row in dataReader:
            kinesis.put_record(StreamName=KINESIS_STREAM_NAME, Data=json.dumps(row), PartitionKey='0')
            break
        f.close() 




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Missing arguments"
        sys.exit(-1)
    if len(sys.argv) > 2:
        print "Extra arguments"
        sys.exit(-1)
    try:
        fileName = sys.argv[1]
        main(fileName)
    except Exception as e:
        raise e
