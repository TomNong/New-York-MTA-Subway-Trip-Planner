#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************
# Creating aws machine learning model
# This program uploads the finalData.csv file to S3, and used it as a data source to train a binary 
# classification model
# USAGE python createAMLModel.py finalData.csv
import time,sys,random

import boto3

import S3

sys.path.append('../utils')
import aws

TIMESTAMP  =  time.strftime('%Y-%m-%d-%H-%M-%S')
S3_BUCKET_NAME = 'mtaedisondata'
S3_FILE_NAME = 'finalData.csv'
S3_URI = "s3://{0}/{1}".format(S3_BUCKET_NAME, S3_FILE_NAME)
DATA_SCHEMA = "aml.csv.schema"


def createDataSourceFromS3(amlClient,dsType,begin,end,computeStats):
    # In order to create data source from S3, we need to give a unique model id ( hence timestamp)
    # S3 URI and schema file.
    modelId = "ds-mtaPredictions-{0}-{1}".format(dsType,TIMESTAMP)
    dataSpec = {}
    dataSpec['DataLocationS3'] = S3_URI

    with open(DATA_SCHEMA) as schemaFile:
        dataSpec['DataSchema'] = schemaFile.read()
        schemaFile.close()

    dataSpec['DataRearrangement'] = '{{"randomSeed":"0","splitting":{{"percentBegin":{0},"percentEnd":{1}}}}}'.format(
       begin, end)
     
    amlClient.create_data_source_from_s3(DataSourceId=modelId,DataSpec=dataSpec,ComputeStatistics=computeStats)
    return modelId

def pollUntilReady(aml,evalId):
    delay = 2
    while True:
        evaluation = aml.get_evaluation(EvaluationId=evalId)
        if evaluation['Status'] in ['COMPLETED', 'FAILED', 'INVALID']:
            return
        sys.stdout.write(".")
        sys.stdout.flush()
        delay *= random.uniform(1.1, 2.0)
        time.sleep(delay)

def main(trainingData):
    # Create an instance of  S3 class ( S3.py)
    s3 = S3.S3(trainingData)
    # Upload data to S3
    s3.uploadData()

    # AWS ML client
    aml = aws.getClient('machinelearning','us-east-1')

    # Check if aml has permission to the s3 bucket
    #s3.checkBucketPolicy()

    # Create training and evaluation data source
    trainingId = createDataSourceFromS3(aml,"training",0,70,True)
    evaluationId = createDataSourceFromS3(aml,"evaluation",70,100,False)

    # create ml model
    mlModelId = "ml-mtaPredictions-{0}".format(TIMESTAMP)
    # NOTE : In ML model target field( label) should be 0 or 1 , any other label will give error 
    aml.create_ml_model(MLModelId=mlModelId, MLModelType="BINARY", TrainingDataSourceId=trainingId)
    evalMlId = "ev-ml-mtaPredictions-{0}".format(TIMESTAMP)
    # create an ml evaluation using the evaluation data set
    aml.create_evaluation(EvaluationId=evalMlId, MLModelId=mlModelId, EvaluationDataSourceId=evaluationId)	

    # Poll to check if model is ready
    pollUntilReady(aml,evalMlId)
    print("done")
    evaluation = aml.get_evaluation(EvaluationId=evalMlId)
    print("Performance metric on the evaluation dataset: Binary AUC: " + str(evaluation['PerformanceMetrics']['Properties']))




if __name__ == "__main__":
	trainingData = sys.argv[1]
	main(trainingData)





