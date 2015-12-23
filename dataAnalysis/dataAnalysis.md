
Data Analysis
===================

There are four steps to the data analysis we do in this project.
In the demo given in directory dataAnalysis, we try to build a binary classification ML model.

1.	Gather data (**gatherData.py**) → gathering raw data from MTA feed. 
2.	Cleaning up data (**buildTrainingDataSet.py**) → clean up and extract relevant information from data in step 1. 
3.	Train AWS ML model (**createAMLModel.py**) → Using data from step 2, we train a binary classification model.
4.	Predicting in real time (**pushToKinesis.py**) → Push unlabeled data to kinesis. There is an AWS Lambda function set up to (In directory lambdaCode **lambdaFunction.js**) trigger when there is an activity in kinesis. This function calls AWS ML endpoint to get a prediction for the label. 

### Gather Data

Usage ***python gatherData.py < filename > < numberofiterations >***

***filename***  → Name of the file to which the data is saved. Format is .csv

***numberofiterations*** → Number of times the MTA feed is accessed. There is a sleep period of 40 seconds between iterations. MTA feed is updated every 30 seconds, hence the sleep period.

This program also accesses ***config.txt*** containing AWS account related fields. Details about this can be found in section AWS Account Setup.

 Program calls mtaUpdates(***../utils/mtaUpdates.py***) to get data from MTA feed. Refer the code comments to understand the logic.

###Clean up data

Usage ***python buildTrainingDataSet.py < filename >***

***filename***  → Name of the file from gather data step. Please input filename with .csv extension.

Our goal here is to get the following values to train ML model.

*delta* → in seconds. Difference between time a which local train reaches first express station and time at which express train reaches first express station after starting point. 

*time* → Time of day at which local train reaches first express station after starting point.
Since this is based on UTC it doesn’t make sense to use this value as a parameter to train the model.  We convert it into time of day( in seconds). So this value could be between 0 and 86400(24x60x60).

*day* → Day of the week

*first* → this value indicates which  train reaches the destination first. We use 0 for express train and 1 for local trains. This is also the target label for the model.  AWS ML takes only 0 and 1 as labels for binary classification.

We make use of python library pandas to clean up the data. Using pandas library, read the csv file to a data frame. In first step, when MTA feed is accessed multiple times resulting in duplicate entries for the same trip. However, we also write timestamp int the csv file. Now we can get rid of all the old entries.  If we do this in step 1, the program runs very slow. It is faster to do this in the second step. 

Code is heavily commented. Please refer to understand the logic.

###	Training ML model

Usage ***python createAMLModel.py finalData.csv***

***finalData.csv*** is the file to which step 2 saves data.

This step uploads the data to S3 and trains a binary classification model using AWS ML APIs.  Once this code finishes running, we can use the model to do real time prediction. 

Setting up S3 and AML is explained in section AWS Account Setup. S3 bucket name should be **mtaedisondata**. 

>**Note:** You will need to go to AWS ML console and select the ML model you trained and enable real time prediction. Under predictions there is a create endpoint button. Don’t forget to disable it when you are not using it. AWS charges for every hour the end point is active.

###Predict in real time

Usage ***python pushToKinesis.py finalData.csv***

***finalData.csv*** is the file to which step 2 saves data. Ideally we should get data from MTA feed and send to kinesis. Kinesis will trigger a lambda function (**../lambdaCode/lambdaFunction.js**). This code sends the data to AWS ML for prediction. In this code , we are just removing the label first and sending to ML for prediction. 

Setting up kinesis and lambda is explained in section AWS Account Setup. For lambda function, the trigger should be selected as kinesis,node.js. Kinesis stream name should be **mtaStream**. 

> ***Note:*** lambdaFunction.js  should be copy pasted to the AWS lambda console.  
