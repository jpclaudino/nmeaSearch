__author__ = 'spi'

import os
from argparse import ArgumentParser
from haversine import haversine
from fileUtil import *
from math import radians, cos, sin, asin, sqrt, degrees
import binascii
import sys
import datetime


AVG_EARTH_RADIUS = 6371
DECIMALSIZE = 50
BYTERANGE = 100
#degreeSign = b'º'



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

class NotFloatCoordinate(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getLimits(point,distance):
    northLimit = haversine_getLatitude(point,distance)
    southLimit = haversine_getLatitude(point,-distance)
    eastLimit = haversine_getLongitude(point,distance)
    westLimit = haversine_getLongitude(point,-distance)
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
        asciiDegreesList.append(degree.encode(ASCII))
    return asciiDegreesList

def getUTFDegrees(degrees):
    utfDegreesList = []
    for degree in degrees:
        utfDegreesList.append(degree.encode(UTF16))
    return utfDegreesList

def checkDegrees(degreeDownLimit,degreeUpLimit, piece, offset,encoding):
    try:
        stringDegreeDownLimit = degreeDownLimit.decode(encoding)
        intDegreeDownLimit = int(stringDegreeDownLimit)
        stringDegreeUpLimit = degreeUpLimit.decode(encoding)
        intDegreeUpLimit = int(stringDegreeUpLimit)
        for intDegree in range(intDegreeDownLimit,intDegreeUpLimit+1):
            stringDegree = intDegree.__str__()
            bytesDegree = stringDegree.encode(encoding)
            tempOffset = offset
            isValidDegree = True
            for byteDegree in bytesDegree:
                if byteDegree != piece[tempOffset]:
                    isValidDegree = False
                    break
                tempOffset += 1
            if isValidDegree:
                return piece[offset:tempOffset]
        raise CoordinateNotFound("Degree not found.")
    except:
        raise CoordinateNotFound("Degree not found.")

def checkLimits(stringLatitude,stringLongitude,limits):
    try:
        floatLatitude = float(stringLatitude)
        floatLongitude = float(stringLongitude)
        northLimit,southLimit,eastLimit,westLimit = limits
        if( (floatLatitude < northLimit) and (floatLatitude > southLimit) and (floatLongitude < eastLimit) and (floatLongitude > westLimit) ):
            return True
        else:
            return False
    except:
        return False

def getMessage(offset,piece,degreeList,limits,encoding):
    northDegree = degreeList[0]
    southDegree = degreeList[1]
    eastDegree = degreeList[2]
    westDegree = degreeList[3]
    latitudeDegree = checkDegrees(southDegree,northDegree, piece, offset,encoding)
    latitude = getDecimalDegreeCoordinate(latitudeDegree,offset,piece,encoding)
    offsetNewPiece = 0
    newPiece = getNewPiece(offset, piece)
    longitude = None
    longitudesList = []
    while (offsetNewPiece < len(newPiece)):
        try:
            longitudeDegree = checkDegrees(westDegree,eastDegree, newPiece, offsetNewPiece,encoding)
            longitude = getDecimalDegreeCoordinate(longitudeDegree,offsetNewPiece,newPiece,encoding)
            longitudesList.append((longitude,abs((BYTERANGE/2)-offsetNewPiece)))
        except:
            pass
        offsetNewPiece += 1
    if not longitudesList:
        raise CoordinateNotFound("Longitude not found.")
    else:
        longitude = getBestLongitude(longitudesList)
        stringLatitude = intListToString(latitude,encoding)
        stringLongitude = intListToString(longitude,encoding)
        if(checkLimits(stringLatitude,stringLongitude,limits)):
            print(stringLatitude + "  " + stringLongitude)
            return stringLatitude,stringLongitude,newPiece
        else:
            raise NotFloatCoordinate("Latitude and longitude must be in decimal degrees")


def getBestLongitude(longitudesList):
    distance = BYTERANGE
    minLong = None
    for longitude in longitudesList:
        if(longitude[1] < distance):
            minLong =  longitude[0]
            distance = longitude[1]
    return minLong

def intListToString(bytelist,encoding):
    frame = bytearray()
    for intByte in bytelist:
        frame.append(intByte)
    return frame.decode(encoding)

def getNewPiece(offset, piece):
    if(offset < BYTERANGE):
        return piece[0:offset + BYTERANGE]
    return piece[offset - BYTERANGE:offset + BYTERANGE]

def getDecimalDegreeCoordinate(degree,offset,piece,encoding):
    coordinateByteArray = []
    tempOffset = offset
    for byteDegree in degree:
        coordinateByteArray.append(piece[tempOffset])
        tempOffset += 1
    if( encoding == ASCII):
        getDecimalDegreeCoordinateASCII(coordinateByteArray, piece, tempOffset)
    else:
        getDecimalDegreeCoordinateUTF(coordinateByteArray, piece, tempOffset)
    return coordinateByteArray

def getDecimalDegreeCoordinateASCII(coordinateByteArray, piece, tempOffset):
    if (piece[tempOffset] == pointSign[0]):
        coordinateByteArray.append(piece[tempOffset])
        count = 0
        while (count < DECIMALSIZE):
            tempOffset += 1
            if (isNumber(piece[tempOffset])):
                coordinateByteArray.append(piece[tempOffset])
                count += 1
            else:
                if (count == 0):
                    raise CoordinateNotFound("Message without decimal part")
                else:
                    break
    else:
        raise CoordinateNotFound("Message without . sign")

def getDecimalDegreeCoordinateUTF(coordinateByteArray, piece, tempOffset):
    if (piece[tempOffset] == pointSign[0] and piece[tempOffset + 1] == zeroSign[0]):
        coordinateByteArray.append(piece[tempOffset])
        coordinateByteArray.append(piece[tempOffset + 1])
        count = 0
        while (count < DECIMALSIZE):
            tempOffset += 2
            if (isNumber(piece[tempOffset]) and piece[tempOffset + 1] == zeroSign[0]):
                coordinateByteArray.append(piece[tempOffset])
                coordinateByteArray.append(piece[tempOffset + 1])
                count += 1
            else:
                if (count == 0):
                    raise CoordinateNotFound("Message without decimal part")
                else:
                    break
    else:
        raise CoordinateNotFound("Message without . sign")

def isNumber(byte):
    for number in numbers:
        if (byte == number):
            return True
    return False

def searchCoordinates(piece,limits,asciiDegreesList,utfDegreesList):
    offset = 0
    messageListASCII = []
    messageListUTF = []
    while offset < len(piece):
        if(isNumber(piece[offset]) or piece[offset] == negativeSign[0] ):
            try:
                try:
                    messageListASCII.append(getMessage(offset,piece,asciiDegreesList,limits,ASCII))
                except:
                    messageListUTF.append(getMessage(offset,piece,utfDegreesList,limits,UTF16))
            except:
                pass
        offset += 1
    return messageListASCII,messageListUTF

def stringSearch(coordinate,distance,basepath):
    print("Starting GPS strings search!")
    print(datetime.datetime.now())
    try:
        fin = open(basepath, "rb")
        foutGPX = open(basepath + "_" + StringGPXFile,'wb')
        foutLOG = open(basepath + "_" + StringLOGFile,'wb')
        foutMemoryLOG = open(basepath + "_" + StringMemoryLOGFile,'wb')
    except:
        print("File not Found")
        exit(0)
    listUTF, listASCII = [],[]
    limits = getLimits(coordinate,distance)
    degreesFromLimits = getDegreesFromLimits(limits)
    stringDegreesFromLimits = getStringDegrees(degreesFromLimits)
    asciiDegreesList = getASCIIDegrees(stringDegreesFromLimits)
    utfDegreesList = getUTFDegrees(stringDegreesFromLimits)
    for piece in read_in_chunks(fin):
        lASCII,lUTF = searchCoordinates(piece,limits,asciiDegreesList,utfDegreesList)
        listUTF = listUTF + lUTF
        listASCII = listASCII + lASCII
    messages = listASCII+listUTF
    for message in messages:
        print(message.__str__())
    buildGPXfromCoordinatesList(foutGPX,messages)
    buildLogFromCoordinatesList(foutLOG,messages)
    buildMemoryLogFromCoordinatesList(foutMemoryLOG,messages)
    fin.close()
    foutGPX.close()
    foutLOG.close()
    foutMemoryLOG.close()
    print(datetime.datetime.now())
    print("GPS sentences write to gpx and log files ")

def main(argv):
    print("Starting GPS Data (coordinates in decimal degrees format) recovery!")
    print(datetime.datetime.now())
    # parser options
    parser = ArgumentParser(description='GPS Data Recovery')
    parser.add_argument(dest='infile', help="The argument needs to be a dump file.")
    parser.add_argument('-d', '--distance', dest='distance', help="Distance in km")
    parser.add_argument('-b', '--bytes', dest='bytes', help="bytes range")
    parser.add_argument('-la', '--latitude',  dest='latitude', help="Latitude in decimal degrees")
    parser.add_argument('-lo', '--longitude',  dest='longitude', help="Longitude in decimal degrees")
    options = parser.parse_args()
    # checks for the input file
    if options.infile is None:
        parser.print_help()
        sys.exit(1)
    if not os.path.exists(options.infile):
        print('Error: "{0}" file is not found!'.format(options.infile))
        sys.exit(1)
    if not options.distance.isdigit():
        print('Error: distance must be in km!'.format(options.infile))
        sys.exit(1)
    if not options.bytes.isdigit():
        print('Error: bytes must be an integer!'.format(options.infile))
        sys.exit(1)
    else:
        BYTERANGE = int(options.bytes)
    try:
        coordinates = (float(options.latitude),float(options.longitude))
    except:
        print('Error: latitude and longitude must be in decimal degrees!'.format(options.infile))
        sys.exit(1)
    stringSearch(coordinates,int(options.distance),options.infile)
    print(datetime.datetime.now())
    print("Nmea sentences write to gpx and log files ")

if __name__ == '__main__':
    main(sys.argv[1:])

#print("-15.817431, -47.930934")
#print(haversine_getLatitude((-15.817431, -47.930934), 0.5).__str__() + ",-47.930934")
#print(haversine_getLatitude((-15.817431, -47.930934), -0.5).__str__() + ",-47.930934")
#print("-15.817431," + haversine_getLongitude((-15.817431, -47.930934), 0.5).__str__())
#print("-15.817431," + haversine_getLongitude((-15.817431, -47.930934), -0.5).__str__())

#print(limits)

#binascii.hexlify(asciiDegreesList[0])
#binascii.hexlify(utfDegreesList[0])
#sys.getsizeof(utfDegreesList[0])

#stringSearch((-15.817431, -47.930934),100,"F:/Mestrado/Dumps/z2 - Waze Sem Desligar/1.raw")
#stringSearch((-15.817431, -47.930934),100,"F:/Mestrado/Dumps/Tablet -  Google Maps - Desligando Location/1.raw")
#stringSearch((-15.817431, -47.930934),100,"D:/2016/15-34591-1-CELULAR-ROTA-GOOGLE-MAPS/UFED/Samsung GSM GT-I9300 Galaxy S III 2016_04_13 (001)/Physical Boot Loader (Recommended) 01/DumpData.bin")

#stringSearch((-15.817431, -47.930934),100,"F:/gps/coordenadasUTF.img")