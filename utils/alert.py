# Storing alerts from the feed
class alert(object):
    alertMessage = None
    tripId = []
    routeId  = {}
    startDate = {}
    def __init__(self):
        self.tripId = []
        self.routeId = {}
        self.startDate = {}