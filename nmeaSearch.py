__author__ = 'Claudino'

from argparse import ArgumentParser
import sys
import os
import pynmea2
import datetime
import gpxpy
import gpxpy.gpx

GPXFile = "NMEA.gpx"
LOGFile = "NMEA.log"
CoordinatesFile = "Coordinates .log"
nmeaGPRMC_UTF16 = b'$\x00G\x00P\x00R\x00M\x00C\x00'
nmeaGPGGA_UTF16 = b'$\x00G\x00P\x00G\x00G\x00A\x00'
nmeaGPRMC_ASCII = b'$GPRMC'
nmeaGPGGA_ASCII = b'$GPGGA'


class BadMessage(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def findCheckSum(offset,pieceOfFile,isUTF16):
    # Find marker (*)
    end = offset + 200
    while(offset < end):
        checksum = pieceOfFile[offset]
        if checksum == 42:
            if(isUTF16):
                return offset + 6
            else:
                return offset + 3
        offset += 1
    return 0

def parseNmea(pieceOfFile):
    offset = 0
    messageListGPRMC_UTF16 = []
    messageListGPGGA_UTF16 = []
    messageListGPRMC_ASCII = []
    messageListGPGGA_ASCII = []
    while offset < len(pieceOfFile):
        dollarSign = pieceOfFile[offset]
        # Dollar sign is the starting character of the message
        if(dollarSign == 36):
            try:
                type = findMessageType(offset,pieceOfFile)
                if type == 1:
                    messageListGPRMC_UTF16.append(getMessageUTF16(offset, pieceOfFile))
                elif type == 2:
                    messageListGPGGA_UTF16.append(getMessageUTF16(offset, pieceOfFile))
                elif type == 3:
                    messageListGPRMC_ASCII.append(getMessageASCII(offset, pieceOfFile))
                elif type == 4:
                    messageListGPGGA_ASCII.append(getMessageASCII(offset, pieceOfFile))
            except:
                pass
        offset += 1
    return messageListGPRMC_UTF16,messageListGPGGA_UTF16,messageListGPRMC_ASCII,messageListGPGGA_ASCII

def getMessageUTF16(offset, pieceOfFile):
    try:
        messageSize = findCheckSum(offset, pieceOfFile,True)
        if messageSize != 0:
            nmeaMessage = pieceOfFile[offset:messageSize]
            nmeaUTF16Message = nmeaMessage.decode('utf-16-le')
            nmeaASCIIMessage = nmeaUTF16Message.encode('ASCII', 'ignore')
            msg = pynmea2.parse(nmeaASCIIMessage.decode())
            return msg
        else:
            raise BadMessage("UTF-16 message not found!")
    except:
        raise BadMessage("UTF-16 message not found!")


def getMessageASCII(offset, pieceOfFile):
    try:
        messageSize = findCheckSum(offset, pieceOfFile, False)
        if messageSize != 0:
            nmeaMessage = pieceOfFile[offset:messageSize]
            msg = pynmea2.parse(nmeaMessage.decode())
            return msg
        else:
            raise BadMessage("ASCII message not found!")
    except:
        raise BadMessage("ASCII message not found!")


def findMessageType(offset,pieceOfFile):
        try:
            pieceUTF16 = pieceOfFile[offset:offset + 12]
            if pieceUTF16 == nmeaGPRMC_UTF16:
                return 1 # Type GPRMC encoded in UTF16
            if pieceUTF16 == nmeaGPGGA_UTF16:
                return 2 # Type GPGGA encoded in UTF16
            pieceASCII = pieceOfFile[offset:offset + 6]
            if pieceASCII == nmeaGPRMC_ASCII:
                return 3 # Type GPRMC encoded in ASCII
            if pieceASCII == nmeaGPGGA_ASCII:
                return 4 # Type GPGGA encoded in ASCII
        except:
                return 0
        return 0

def read_in_chunks(file_object, chunk_size=1024000):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def gpsFinder(basepath):
    try:
        fin = open(basepath, "rb")
        foutGPX = open(basepath + "_" + GPXFile,'wb')
        foutLOG = open(basepath + "_" + LOGFile,'wb')
        foutCoordinates = open(basepath + "_" + CoordinatesFile,'wb')
    except:
        print("File not Found")
        exit(0)
    listGPRMC, listGPGGA, listGPRMC_UTF16,listGPGGA_UTF16,listGPRMC_ASCII,listGPGGA_ASCII = [],[],[],[],[],[]
    for piece in read_in_chunks(fin):
        lGPRMC_UTF16,lGPGGA_UTF16,lGPRMC_ASCII,lGPGGA_ASCII = parseNmea(piece)
        listGPRMC_UTF16 = listGPRMC_UTF16 + lGPRMC_UTF16
        listGPGGA_UTF16 = listGPGGA_UTF16 + lGPGGA_UTF16
        listGPRMC_ASCII = listGPRMC_ASCII + lGPRMC_ASCII
        listGPGGA_ASCII = listGPGGA_ASCII + lGPGGA_ASCII
    listGPRMC = listGPRMC_UTF16 + listGPRMC_ASCII
    listGPGGA = listGPGGA_UTF16 + listGPGGA_ASCII
    buildLog(foutLOG,listGPGGA, listGPGGA_ASCII, listGPGGA_UTF16, listGPRMC, listGPRMC_ASCII, listGPRMC_UTF16)
    try:
        sortedListGPRMC = sorted(listGPRMC+listGPGGA,key=lambda msg: msg.timestamp)
        buildGPX(foutGPX,sortedListGPRMC)
        buildCoordinatesLog(foutCoordinates,sortedListGPRMC)
    except:
        buildGPX(foutGPX,listGPRMC+listGPGGA)
        buildCoordinatesLog(foutCoordinates,listGPRMC+listGPGGA)
    fin.close()
    foutGPX.close()
    foutLOG.close()
    foutCoordinates.close()

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

def buildLog(wfile,listGPGGA, listGPGGA_ASCII, listGPGGA_UTF16, listGPRMC, listGPRMC_ASCII, listGPRMC_UTF16):
    countMessages(listGPGGA, listGPGGA_ASCII, listGPGGA_UTF16, listGPRMC, listGPRMC_ASCII, listGPRMC_UTF16, wfile)
    for msg in listGPRMC:
        printMsg(wfile,msg, True)
    for msg in listGPGGA:
        printMsg(wfile,msg, False)

def filterList(list):
    for msg in list:
        if msg.is_valid: yield msg

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

def main(argv):
    print("Starting NMEA sentences recovery!")
    print(datetime.datetime.now())
    # parser options
    parser = ArgumentParser(description='GPS Data Recovery')
    parser.add_argument(dest='infile', help="The argument needs to be a dump file.")
    options = parser.parse_args()
    # checks for the input file
    if options.infile is None:
        parser.print_help()
        sys.exit(1)
    if not os.path.exists(options.infile):
        print('Error: "{0}" file is not found!'.format(options.infile))
        sys.exit(1)
    gpsFinder(options.infile)
    print(datetime.datetime.now())
    print("Nmea sentences write to gpx and log files ")
    
if __name__ == '__main__':
    main(sys.argv[1:])