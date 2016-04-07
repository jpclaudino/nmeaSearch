__author__ = 'spi'

from haversine import haversine
from fileUtil import read_in_chunks
from math import radians, cos, sin, asin, sqrt, degrees
import binascii
import sys

AVG_EARTH_RADIUS = 6371
degreeSign = b'º'
pointSign = b'.'


def haversine_getLatitude(point1, d):
    """ Calculates the latitude of a point distant "d" kilometes from the reference point, passed as a parameter.

    :input: one tuple, containing the latitude and longitude of a fixed point
    in decimal degrees, and the distance to the next point (which has the same longitude of the input tuple), in kilometers.

    :output: Returns latitude of a the point in degrees.

    """
    # unpack latitude/longitude
    lat1, lng1 = point1

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1 = map(radians, (lat1, lng1))

    # calculate latitude
    lat2 = (2 * asin( (sin(d/ (2*AVG_EARTH_RADIUS) )) ) ) + lat1

    return degrees(lat2)

def haversine_getLongitude(point1, d):
    """ Calculates the longitude of a point distant "d" kilometes from the reference point, passed as a parameter.

    :input: one tuple, containing the latitude and longitude of a fixed point
    in decimal degrees, and the distance to the next point (which has the same latitude of the input tuple), in kilometers.

    :output: Returns latitude of a the point in degrees.

    """
    # unpack latitude/longitude
    lat1, lng1 = point1

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1 = map(radians, (lat1, lng1))

    # calculate latitude
    lng2 = (2 * asin( (sin(d/ (2*AVG_EARTH_RADIUS) )) / (cos(lat1)) ) )  + lng1

    return degrees(lng2)

class CoordinateNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

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

def getStringDegrees(degrees):
    stringDegreesList = []
    for degree in degrees:
        stringDegreesList.append(str(degree))
    return stringDegreesList

def getASCIIDegrees(degrees):
    asciiDegreesList = []
    for degree in degrees:
        asciiDegreesList.append(degree.encode('ASCII'))
    return asciiDegreesList

def getUTFDegrees(degrees):
    utfDegreesList = []
    for degree in degrees:
        utfDegreesList.append(degree.encode('utf-16-le'))
    return utfDegreesList

def getMessageASCII(offset,piece,asciiDegreesList,limits):
    northDegree = asciiDegreesList(0)
    southDegree = asciiDegreesList(1)
    westDegree = asciiDegreesList(2)
    eastDegree = asciiDegreesList(3)
    tempOffset = offset
    if(checkDegrees(northDegree, piece, tempOffset)) :
        print(offset)
        print(tempOffset)
    elif (checkDegrees(southDegree, piece, tempOffset)):
        print(offset)
        print(tempOffset)

def checkDegrees(degree, piece, tempOffset):
    for byteDegree in degree:
        if byteDegree != piece[tempOffset]:
            return False
        tempOffset += 1
    return True

def getMessageUTF(offset,piece,asciiDegreesList,limits):
    northDegree = asciiDegreesList(0)
    southDegree = asciiDegreesList(1)
    westDegree = asciiDegreesList(2)
    eastDegree = asciiDegreesList(3)

def searchCoordinates(coordinate,distance,piece):
    limits = getLimits((coordinate.latitude, coordinate.longitude),distance)
    degreesFromLimits = getDegreesFromLimits(limits)
    stringDegreesFromLimits = getStringDegrees(degreesFromLimits)
    asciiDegreesList = getASCIIDegrees(stringDegreesFromLimits)
    utfDegreesList = getUTFDegrees(stringDegreesFromLimits)
    offset = 0
    messageListASCII = []
    messageListUTF = []
    while offset < len(piece):
        try:
            messageListASCII.append(getMessageASCII(offset,piece,asciiDegreesList,limits))
            messageListUTF.append(getMessageUTF(offset,piece,utfDegreesList,limits))
        except:
            pass
        offset += 1
    return messageListASCII,messageListUTF

def stringSearch(coordinate,distance,basepath):
    try:
        fin = open(basepath, "rb")
    except:
        print("File not Found")
        exit(0)
    for piece in read_in_chunks(fin):
        searchCoordinates(coordinate,distance,piece)
    fin.close()


#print("-15.817431, -47.930934")
#print(haversine_getLatitude((-15.817431, -47.930934), 0.5).__str__() + ",-47.930934")
#print(haversine_getLatitude((-15.817431, -47.930934), -0.5).__str__() + ",-47.930934")
#print("-15.817431," + haversine_getLongitude((-15.817431, -47.930934), 0.5).__str__())
#print("-15.817431," + haversine_getLongitude((-15.817431, -47.930934), -0.5).__str__())

#print(limits)

#binascii.hexlify(asciiDegreesList[0])
#binascii.hexlify(utfDegreesList[0])
#sys.getsizeof(utfDegreesList[0])