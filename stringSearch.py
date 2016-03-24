from haversine import haversine, haversine_getLatitude, haversine_getLongitude


__author__ = 'spi'




print("-15.817431, -47.930934")
print( haversine_getLatitude((-15.817431, -47.930934), 0.5).__str__() + ",-47.930934")
print(haversine_getLatitude((-15.817431, -47.930934), -0.5).__str__() + ",-47.930934")
print("-15.817431," + haversine_getLongitude((-15.817431, -47.930934), 0.5).__str__())
print("-15.817431," + haversine_getLongitude((-15.817431, -47.930934), -0.5).__str__())

def getLimits(point,distance):
    northLimit = haversine_getLatitude(point,distance)
    southLimit = haversine_getLatitude(point,-distance)
    westLimit = haversine_getLongitude(point,distance)
    eastLimit = haversine_getLongitude(point,-distance)
    return northLimit,southLimit,eastLimit,westLimit

def getDegreesFromLimits(limits):
    degreesList = []
    for limit in limits:
        degreesList.append(int(limit))
    return degreesList

limits = getLimits((-15.817431, -47.930934),50)
print(limits)
degreesFromLimits = getDegreesFromLimits(limits)
print(degreesFromLimits)