import mraa
import time
import boto
import boto.dynamodb2


# Provide account related details here
ACCOUNT_ID = 'xxxx'
IDENTITY_POOL_ID = 'xxxx'
ROLE_ARN = 'xxxx'
KINESIS_STREAM_NAME = 'x'
DYNAMODB_TABLE_NAME = 'x'
PARTITION_KEY = 'partitionKey'
DEVICE_ID = 'tempSensor'
DELAY = 0.1

temp_sensor = mraa.Aio(1)
push_button = mraa.Gpio(8)
push_button.dir(mraa.DIR_IN)
buzzer = mraa.Gpio(6)
buzzer.dir(mraa.DIR_OUT)

mode = 0 # mode is either writing to Kinesis or to DynamoDB

# Use cognito to get an identity.
cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])
sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN, "XX", oidc['Token'])

# Prepare Kinesis client
client_kinesis = boto.connect_kinesis(
    aws_access_key_id=assumedRoleObject.credentials.access_key,
    aws_secret_access_key=assumedRoleObject.credentials.secret_key,
    security_token=assumedRoleObject.credentials.session_token)

# Prepare DynamoDB client
client_dynamo = boto.dynamodb2.connect_to_region(
    'us-east-1',
    aws_access_key_id=assumedRoleObject.credentials.access_key,
    aws_secret_access_key=assumedRoleObject.credentials.secret_key,
    security_token=assumedRoleObject.credentials.session_token)
from boto.dynamodb2.table import Table
table_dynamo = Table(DYNAMODB_TABLE_NAME, connection=client_dynamo)


def get_time () :
    return str(round(time.time() * 1000))


def get_core_data (sensor) :
    temp = sensor.read()
    #resistance = (1023-v)*10000.0/v
    #temp = 1/(math.log(resistance/10000.0)/B+1/298.15)-273.15
    print "Temperature now is " + str(temp)
    return "[{\"TemperatureSensor\": {\"temperature\":" +str(temp) + "}}]"



def get_kinesis_data (sensor) :
    return "{\"deviceid\": \""+DEVICE_ID+"\", \"time\": " + str(get_time()) + ", \"sensors\":"+get_core_data(sensor)+"}"


def change_mode (mode) :
    newmode = mode + 1
    if (newmode%2 == 1):
        print "Running in Kinesis mode"
    else:
        print "Running in DynamoDB mode"
    for x in range (0, 2 - (newmode % 2)) :
        buzzer.write(1)
        time.sleep(0.1)
        buzzer.write(0)
        time.sleep(0.1)
    return newmode


# -----------------


mode = change_mode(mode)
count = 1

while True:
    time.sleep(DELAY)
    # if I'm pressing the button, cycle mode
    if push_button.read(): 
        mode = change_mode(mode)
    if (mode%2 == 1):
        # if mode = 1 write data to kinesis
        client_kinesis.put_record(KINESIS_STREAM_NAME, get_kinesis_data(temp_sensor), PARTITION_KEY)
    else:
        count = count + 1
        # Generate a unique id since primary key must be unique. You can also use a random number generator.
        id = str(DEVICE_ID + str(count))
        table_dynamo.put_item(data={"deviceid":id, "time": get_time(), "sensors": get_core_data(temp_sensor)})
