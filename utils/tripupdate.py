from collections import OrderedDict
# Storing trip related data
# Note : some trips wont have vehicle data
class tripupdate(object):
	def __init__(self):
	    self.tripId = None
	    self.routeId = None
	    self.startDate = None
	    self.direction = None
	    self.vehicleData = None
	    self.futureStops = OrderedDict() # Format {stopId : [arrivalTime,departureTime]}





