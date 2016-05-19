__author__ = 'jpcla_000'

import gpxpy
import gpxpy.gpx


GPXFile = "NMEA.gpx"
LOGFile = "NMEA.log"
StringGPXFile = "StringCoordinates.gpx"
StringLOGFile = "StringCoordinates.log"
StringMemoryLOGFile = "StringCoordinatesMemory.log"
CoordinatesFile = "Coordinates .log"

pointSign = b'.'
negativeSign = b'-'
numbers = b'0123456789'
zeroSign = b'\x00'
ASCII =  'ASCII'
UTF16 = 'utf-16-le'

def read_in_chunks(file_object, chunk_size=1024000):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def buildGPXfromCoordinatesList(wfile,listMessages):
    gpx = gpxpy.gpx.GPX()
    name = 1
    for msg in listMessages:
        if msg != None:
            try:
                gpx_waypoint=gpxpy.gpx.GPXWaypoint(name=name, latitude=msg[0], longitude=msg[1])
                gpx.waypoints.append(gpx_waypoint)
                name += 1
            except:
                pass
    wfile.write(gpx.to_xml().encode('utf-8'))

def buildLogFromCoordinatesList(wfile,listMessages):
    sentence = "latitude,longitude"
    wfile.write(sentence.encode('utf-8'))
    for msg in listMessages:
        if msg != None:
            try:
                sentence = "\n" + str(msg[0]) + "," + str(msg[1])
                wfile.write(sentence.encode('utf-8'))
            except:
                pass

def buildMemoryLogFromCoordinatesList(wfile,listMessages):
    for msg in listMessages:
        try:
            wfile.write(msg.__str__().encode('utf-8'))
        except:
            pass

def buildGPX(wfile,listNMEAMessages):
    gpx = gpxpy.gpx.GPX()
    name = 1
    for msg in listNMEAMessages:
        if msg != None:
            try:
                if msg.latitude != None and msg.longitude != None and  msg.latitude != 0.0 and msg.longitude != 0.0:
                    gpx_waypoint=gpxpy.gpx.GPXWaypoint(name=name, latitude=msg.latitude, longitude=msg.longitude)
                    gpx.waypoints.append(gpx_waypoint)
                    name += 1
            except:
                pass
    wfile.write(gpx.to_xml().encode('utf-8'))

def buildCoordinatesLog(wfile,listNMEAMessages):
    sentence = "latitude,longitude"
    wfile.write(sentence.encode('utf-8'))
    for msg in listNMEAMessages:
        if msg != None:
            try:
                if msg.latitude != None and msg.longitude != None and  msg.latitude != 0.0 and msg.longitude != 0.0:
                    if msg.timestamp != None:
                        sentence = "\n" + str(msg.latitude) + "," + str(msg.longitude) + "," + str(msg.timestamp)
                    else:
                        sentence = "\n" + str(msg.latitude) + "," + str(msg.longitude) + ",0"
                    wfile.write(sentence.encode('utf-8'))
            except:
                pass

def buildLog(wfile,listGPGGA, listGPGGA_ASCII, listGPGGA_UTF16, listGPRMC, listGPRMC_ASCII, listGPRMC_UTF16):
    countMessages(listGPGGA, listGPGGA_ASCII, listGPGGA_UTF16, listGPRMC, listGPRMC_ASCII, listGPRMC_UTF16, wfile)
    for msg in listGPRMC:
        printMsg(wfile,msg, True)
    for msg in listGPGGA:
        printMsg(wfile,msg, False)

def printMsg(wfile,msg,printSpeed):
    try:

        if printSpeed:
            sentence = "\n"+ msg.__str__() + "     -    Speed in Km/h: "  + str(msg.spd_over_grnd * 1.852)
            wfile.write(sentence.encode('utf-8'))
        else:
            sentence = "\n"+ msg.__str__()
            wfile.write(sentence.encode('utf-8'))
    except:
        pass

def countMessages(listGPGGA, listGPGGA_ASCII, listGPGGA_UTF16, listGPRMC, listGPRMC_ASCII, listGPRMC_UTF16, wfile):
    validGPGGAMessages = list(filterList(listGPGGA))
    validGPRMCMessages = list(filterList(listGPRMC))
    wfile.write(("Number of Unicode GPRMC messages: " + str(len(listGPRMC_UTF16))).encode('utf-8'))
    wfile.write(("\nNumber of ASCII GPRMC messages: " + str(len(listGPRMC_ASCII))).encode('utf-8'))
    wfile.write(("\nTotal Number of GPRMC messages: " + str(len(listGPRMC))).encode('utf-8'))
    wfile.write(("\nTotal Number of Valid GPRMC messages: " + str(len(validGPRMCMessages))).encode('utf-8'))
    wfile.write("\n*************************************".encode('utf-8'))
    wfile.write(("\nNumber of Unicode GPGGA messages: " + str(len(listGPGGA_UTF16))).encode('utf-8'))
    wfile.write(("\nNumber of ASCII GPGGA messages: " + str(len(listGPGGA_ASCII))).encode('utf-8'))
    wfile.write(("\nTotal Number of GPGGA messages: " + str(len(listGPGGA))).encode('utf-8'))
    wfile.write(("\nTotal Number of Valid GPGGA messages: " + str(len(validGPGGAMessages))).encode('utf-8'))
    wfile.write("\n*************************************".encode('utf-8'))

def filterList(list):
    for msg in list:
        if msg.is_valid: yield msg

