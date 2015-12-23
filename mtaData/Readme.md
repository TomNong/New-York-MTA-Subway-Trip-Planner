Updating and cleaning Database
===============================

Usage ***python dynamodata.py***

> Note: **MTA Feed API key** -- before running this program, you need to request a API key from MTA website. Once you have it save it in **../key.txt**. Program reads it from file and passes it to **mtaUpdates.py**

This program runs two threads.

1.	Update DB with latest MTA feed information
2. Clean up old entried from DB

### Update DB

Update db thread uses ***mtaUpdates.py*** to get the data from MTA feed. We use dyanmodb to store data. Format of the data written in dynamodb is as follows.

tripId|routeId|startDate|direction|currentStopId|vehicleTimeStamp|futureStops|timestamp|
------|------|-----------|--------|-------------|----------------|-----------|----------|


Primary key is tripId since it is a unique value. timestamp is used to keep track of when the entry was updated last. It is used in determining whether an entry is stale. Update Db thread sleeps for 33 seconds and runs in an infinite loops until program is terminated.

### Cleaning up DB

If the timestamp of an entry is more than 120 seconds older than current time, it will be deleted. clean up db thread scans database for all the stale entries and deletes them. It sleeps for 60 seconds and runs in an infinite loop.

> **Note:** If this is your first time running this program, i.e, currently the db is empty, uncomment line  before starting clean up db thread. This is done so that the clean up thread doesnt start right away. If it starts withouty a sleep period, there is a chance thread throws an error if the update db thread hasnt written anything in dynamodb. Code snippet below.  


```

 #time.sleep(120)
 
 cleanUpDbThread.start()
 
```

> **Note:** Setting up DynamoDB is explained in AWS set up document.

