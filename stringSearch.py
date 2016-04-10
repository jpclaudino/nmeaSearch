__author__ = 'spi'

from haversine import haversine
from fileUtil import read_in_chunks
from math import radians, cos, sin, asin, sqrt, degrees
import binascii
import sys

AVG_EARTH_RADIUS = 6371
DECIMALSIZE = 50
BYTERANGE = 100
#degreeSign = b'º'
pointSign = b'.'
numbers = b'0123456789'


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
    northDegree = asciiDegreesList[0]
    southDegree = asciiDegreesList[1]
    westDegree = asciiDegreesList[2]
    eastDegree = asciiDegreesList[3]
    if(checkDegrees(northDegree, piece, offset)) :
        latitudeDegree = northDegree
    elif (checkDegrees(southDegree, piece, offset)):
        latitudeDegree = southDegree
    else:
        raise CoordinateNotFound("Degree not found.")
    latitude = getDecimalDegreeCoordinate(latitudeDegree,offset,piece)
    offsetNewPiece = 0
    newPiece = getNewPiece(offset, piece)
    while (offsetNewPiece < len(newPiece)):
        longitude = None
        try:
            if(checkDegrees(westDegree, newPiece, offsetNewPiece)) :
                longitudeDegree = westDegree
            elif (checkDegrees(eastDegree, newPiece, offsetNewPiece)):
                longitudeDegree = eastDegree
            else:
                raise CoordinateNotFound("Degree not found.")
            longitude = getDecimalDegreeCoordinate(longitudeDegree,offsetNewPiece,newPiece)
        except:
            pass
        offsetNewPiece += 1
    if (longitude == None):
        raise CoordinateNotFound("Longitude not found.")
    else:
        return latitude,longitude,newPiece


def getNewPiece(offset, piece):
    if(offset < BYTERANGE):
        return piece[0:offset + BYTERANGE]
    return piece[offset - BYTERANGE:offset + BYTERANGE]

def getDecimalDegreeCoordinate(degree,offset,piece):
    coordinateByteArray = []
    tempOffset = offset
    for byteDegree in degree:
        coordinateByteArray.append(piece[tempOffset])
        tempOffset += 1
    if( piece[tempOffset] == pointSign[0] ):
        coordinateByteArray.append(piece[tempOffset])
        count = 0
        while( count < DECIMALSIZE ):
            tempOffset += 1
            if( isNumber(piece[tempOffset]) ):
                coordinateByteArray.append(piece[tempOffset])
                count += 1
            else:
                if (count == 0):
                    raise CoordinateNotFound("Message without decimal part")
                else:
                    break
    else:
        raise CoordinateNotFound("Message without . sign")
    return coordinateByteArray

def isNumber(byte):
    for number in numbers:
        if (byte == number):
            return True
    return False

def checkDegrees(degree, piece, offset):
    tempOffset = offset
    for byteDegree in degree:
        if byteDegree != piece[tempOffset]:
            return False
        tempOffset += 1
    return True

def getMessageUTF(offset,piece,asciiDegreesList,limits):
    northDegree = asciiDegreesList[0]
    southDegree = asciiDegreesList[1]
    westDegree = asciiDegreesList[2]
    eastDegree = asciiDegreesList[3]

def searchCoordinates(coordinate,distance,piece):
    limits = getLimits(coordinate,distance)
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

stringSearch((-15.817431, -47.930934),10,"C:/Users/jpcla_000/Desktop/coordenadas.img")