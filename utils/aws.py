#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# *********************************************************************************************

# Contains all functions needed to get a aws client or resource
# Used in ../dataAnalysis/S3.py and ../dataAnalysis/createAMLModel.py

import boto3
	
COGNITO_ID = "EdisonApp"


def getCredentials():
	# Get AWS account related details
	with open('../../config.txt', 'rb') as configfile:
		ACCOUNT_ID,IDENTITY_POOL_ID,ROLE_ARN = configfile.read().splitlines()
		configfile.close()
	# Use cognito to get an identity from AWS for the application residing on Edison
	# boto3.client function helps you get a client object of any AWS service
	# Here for example we are getting a client object of AWS cognito service
	cognito = boto3.client('cognito-identity','us-east-1') 
	cognito_id = cognito.get_id(AccountId=ACCOUNT_ID, IdentityPoolId=IDENTITY_POOL_ID)
	oidc = cognito.get_open_id_token(IdentityId=cognito_id['IdentityId'])

	    # Similar to the above code, here we are getting a client object for AWS STS service
	sts = boto3.client('sts')
	assumedRoleObject = sts.assume_role_with_web_identity(RoleArn=ROLE_ARN,\
	                     RoleSessionName=COGNITO_ID,\
	                    WebIdentityToken=oidc['Token'])

	    # This contains Access key Id and secret access key and sessiontoken to connect to dynamodb
	credentials = assumedRoleObject['Credentials']
	return credentials


def getResource(resourceName,region):
	credentials = getCredentials()
	resource = boto3.resource(resourceName,
			 region,
	        aws_access_key_id= credentials['AccessKeyId'],
	        aws_secret_access_key=credentials['SecretAccessKey'],
	        aws_session_token=credentials['SessionToken'])
	return resource

def getClient(clientName,region):
	credentials = getCredentials()
	client = boto3.client(clientName,
			 region,
	        aws_access_key_id= credentials['AccessKeyId'],
	        aws_secret_access_key=credentials['SecretAccessKey'],
	        aws_session_token=credentials['SessionToken'])
	return client

