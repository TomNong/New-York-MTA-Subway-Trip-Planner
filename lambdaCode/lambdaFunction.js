
// Code used is from awslab github with slight modifications

console.log("Loading event")
exports.handler = function(event, context) {
  var AWS = require('aws-sdk');
  var ml = new AWS.MachineLearning();
  var endpointUrl = '';
  var mlModelId = 'ml-mtaPredictions-2015-12-07-20-19-06';
  var numMessagesToBeProcessed = event.Records.length;
  
  var callPredict = function(mtaData){
    console.log('calling predict');
        ml.predict(
            {
                Record : mtaData,
                PredictEndpoint : endpointUrl,
                MLModelId: mlModelId
                
            },function(err, data) {
      console.log("hi s")
                if (err) {
                    console.log(err);
                    context.done(null, 'Call to predict service failed.');
                    
                }
                else {
                    console.log('Predict call succeeded');
                    if(data.Prediction.predictedLabel === '1'){
                        console.log("local train reaches first")
                        
                    }
                    else{
                        console.log("express train reaches first")
                        
                    }
        }
                
            });
    }
  
         
  var processRecords = function(){
    for(i = 0; i < numMessagesToBeProcessed; ++i) {
      encodedPayload = event.Records[i].kinesis.data;
      // Amazon Kinesis data is base64 encoded so decode here
      payload = new Buffer(encodedPayload, 'base64').toString('utf-8');
      try {
        parsedPayload = JSON.parse(payload);
        //remove '' and 'first' labels
            delete parsedPayload['first'];
            delete parsedPayload['']
        
        callPredict(parsedPayload);
      }
      catch (err) {
        console.log(err, err.stack);
        context.done(null, "failed payload"+payload);
      }
    }
  }

    var checkRealtimeEndpoint = function(err, data){
    if (err){
      console.log(err);
      context.done(null, 'Failed to fetch endpoint status and url.');
    }
    else {
      var endpointInfo = data.EndpointInfo;
      console.log("end point info is : "+endpointInfo)    
      if (endpointInfo.EndpointStatus === 'READY') {
        endpointUrl = endpointInfo.EndpointUrl;
        console.log('Fetched endpoint url :'+endpointUrl);
        processRecords();
      } else {
        console.log('Endpoint status : ' + endpointInfo.EndpointStatus);
        context.done(null, 'End point is not Ready.');
      }
    }
  };

  ml.getMLModel({MLModelId:mlModelId,Verbose:true},checkRealtimeEndpoint);
  //context.succeed("Successfully processed " + event.Records.length + " record.");
};