from boto import kinesis
import testdata
import json

"""kinesis = kinesis.connect_to_region("eu-west-1")
stream = kinesis.create_stream("EdisonDemo", 1)
kinesis.describe_stream("EdisonDemo")
kinesis.list_streams()
"""
class Users(testdata.DictFactory):
   firstname = testdata.FakeDataFactory('firstName')
   lastname = testdata.FakeDataFactory('lastName')
   age = testdata.RandomInteger(10, 30)
   gender = testdata.RandomSelection(['female', 'male'])


for user in Users().generate(50):
    print user
    kinesis.put_record("EdisonDemo",json.dumps(user),"partitionKey")


shard_id = 'shardId-000000000000'
shard_it = kinesis.get_shard_iterator("EdisonDemo", shard_id, "LATEST")["ShardIterator"]
while True:
    out = kinesis.get_record(shard_it,limit=2)
    print out
    time.sleep(0.2)
