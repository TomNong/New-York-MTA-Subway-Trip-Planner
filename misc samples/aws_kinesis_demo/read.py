from boto import kinesis
import time

# Using boto connect to the region in which your kinesis stream is created
kinesis = kinesis.connect_to_region("eu-west-1")


shard_id = 'shardId-000000000000' 
# Iterator to go throough the latest stream values
shard_it = kinesis.get_shard_iterator("BotoDemo", shard_id, "LATEST")["ShardIterator"]

# Get thed ata 
while True:
    out = kinesis.get_records(shard_it, limit=2)
    shard_it = out["NextShardIterator"]
    print out
    time.sleep(0.3)
