from boto import kinesis
import testdata,json
# Creating fake data
class Users(testdata.DictFactory):
    firstname = testdata.FakeDataFactory("firstName")
    lastname = testdata.FakeDataFactory("lastName")
    age = testdata.RandomInteger(10,30)
    gender = testdata.RandomSelection(['female','male'])

# Using boto connect to the region in which your kinesis stream is created
kinesis = kinesis.connect_to_region("eu-west-1")

for user in Users().generate(50):
    print user
    kinesis.put_record("EdisonDemo", json.dumps(user), "partitionkey")

