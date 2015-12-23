import urllib2,contextlib
from datetime import datetime
from collections import OrderedDict

from pytz import timezone
import gtfs_realtime_pb2
import google.protobuf

import vehicle,alert,tripupdate

class mtaUpdates(object):

    # Do not change Timezone
    TIMEZONE = timezone('America/New_York')
    
    # feed url depends on the routes to which you want updates
    # here we are using feed 1 , which has lines 1,2,3,4,5,6,S
    # While initializing we can read the API Key and add it to the url
    feedurl = 'http://datamine.mta.info/mta_esi.php?feed_id=1&key='
    
    VCS = {1:"INCOMING_AT", 2:"STOPPED_AT", 3:"IN_TRANSIT_TO"}    
    tripUpdates = []
    alerts = []

    def __init__(self,apikey):
        self.feedurl = self.feedurl + apikey

    # Method to get trip updates from mta real time feed
    def getTripUpdates(self):
        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            with contextlib.closing(urllib2.urlopen(self.feedurl)) as response:
                d = feed.ParseFromString(response.read())
        except (urllib2.URLError, google.protobuf.message.DecodeError) as e:
            print "Error while connecting to mta server " +str(e)
	

	timestamp = feed.header.timestamp
        nytime = datetime.fromtimestamp(timestamp,self.TIMEZONE)
	
	for entity in feed.entity:
	    # Trip update represents a change in timetable
	    if entity.trip_update and entity.trip_update.trip.trip_id:
		update = tripupdate.tripupdate()
		update.tripId = entity.trip_update.trip.trip_id
		update.routeId = entity.trip_update.trip.route_id
		update.startDate = entity.trip_update.trip.start_date
		# We can get direction from tripId
		update.direction = update.tripId[10]
		
		# Route id could be 1,2,3,4,5,6 or S.
                # However for S they use  GS
                if update.routeId == 'GS':
                    update.routeId = 'S'
		
		# Create an ordered dictionary
		for stopUpdate in entity.trip_update.stop_time_update:
		    arrivalTime = {"arrivalTime" : stopUpdate.arrival.time}
		    departureTime = {"departureTime" : stopUpdate.departure.time}    
		    update.futureStops[stopUpdate.stop_id] = [arrivalTime, departureTime]
		
		
		self.tripUpdates.append(update)

	    if entity.vehicle and entity.vehicle.trip.trip_id:
	    	v = vehicle.vehicle()
		vehicleData = entity.vehicle
		tripId = vehicleData.trip.trip_id
		v.currentStopNumber = vehicleData.current_stop_sequence
		v.currentStopId = vehicleData.stop_id
		v.timestamp   =  vehicleData.timestamp
		if not vehicleData.current_status:
		    v.currentStopStatus = self.VCS[1]
		else:
		    v.currentStopStatus = self.VCS[vehicleData.current_status]
		# Find the tripUpdate object with the exact tripId
	    	tripUpdateObject = next((trip for trip in self.tripUpdates if trip.tripId == tripId), None)
		tripUpdateObject.vehicleData = v
	    
	    if entity.alert:
                a = alert.alert()
		for item in entity.alert.informed_entity:
		    trip = item.trip.trip_id
                    a.tripId.append(trip)
                    a.routeId[trip] = item.trip.route_id  
		a.alertMessage = entity.alert.header_text
		self.alerts.append(a)

	return self.tripUpdates


    # END OF getTripUpdates method
