Trip planning (mta.py)
===================

Usage ***python mta.py***

Once you run the code you will be presented with three options.

```
   Available Commands are : 
   1. plan trip"
   2. send me list of options for the trip
   3. exit
```

### Plan Trip

If you select option 1, you will need to enter stop ids for source stop,destination stop and direction.Results will be shown in the command line interface. 


> Note: For demonstration purposes currently the code supports only source as 117S (Columbia University) and destination as 127S (42nd station) and direction 'S' (Downtown). Making it generic will need a more complex algorithm and more data about all the stations. I am planning to update it in the future.


Program makes use of data saved in dynamodb table called **mtaData**. It queries the database for current train information and does some simple calculations to find out whether we need to make a switch at the express station.

> Note: dynamodb table is populated using another program called **../mtaData/dynamodata.py**. This code will be run on a server. It needs to be run continuously to get accurate data. 


### Send a List of options for the trip
**Currently not implemented**
>Note: Future plan is to get the phone number from user and SMS a list of trip options. SNS is used to publish these messages.

>  **Setting up dynamodb and SNS is explained in AWS setup section**


