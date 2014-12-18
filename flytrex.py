#!/usr/bin/env python

# Decode FlyTrex files

import math
import struct
from datetime import datetime

filename = '00000004.FPV'

class FlyTrexGPSData(object):
    def __init__(self, time, lat, lon, alt):
        '''
        A FlyTrexGPSData object is the structure to hold a single GPS record
        '''
        self.time=time
        self.lat=lat
        self.lon=lon
        self.alt=alt

    def __str__(self):
        return ",".join(map(str,[self.time, self.lat, self.lon, self.alt]))

class FlyTrexLog(object):
    log = []
    first_packet_offset = 46
    morning_night = 1

    def __init__(self, filename):
        '''
        A FlyTrexLog object is a wrapper around the base .FPV file that 
        flytrex loggers output
        '''
        self.filename=filename
        # Open and read the file
        test_file = open(filename)
        test_data = test_file.read()        
        self.decode(test_data)
        
    def writeCSV(self, filename):
        """ logobj.writeCSV(filename) you need a log object and provide a filename which will be writen
            in the current working directory.
        """
        #print "This is trying to write a CSV!!!!!!!!!"
        import os
        import csv
         
        extra = [
        'extra_column',
        ]
        
        output_directory = os.getcwd() # local working directory

        if filename[-4:].lower() <> ".csv":
            filename = filename+".csv"



        csvfile  = open(os.path.join(output_directory,filename), "wb")
        writer = csv.writer(csvfile, delimiter=',')
        header = ['id','Longitude','Latitude','path']
        # add extra headers if needed
        #header.extend(extra)
        writer.writerow(header)
         
        #print type(self.log)
         
        for x in self.log:
            #print x
            row = str(x).split(',') #[str(id),str(lon),str(lat),str(path)]
            # add extra data if extra headers where used
            #row.extend(extra_out)
            writer.writerow(row)
         
        csvfile.flush()
        csvfile.close()



    def decode_mask(self,data,mask):
        b = bytearray(data)
        length = len(b)
        b2 = bytearray(length)
        #print "len = " + str(len(b))
        for i in range(length):
            #print hex(b[i])
            b2[length - i - 1] = b[i] ^ mask
            #print hex(b2[length - i - 1])
        #for x in b2:
        #    print hex(x)
        return b2
    
    
    def decode(self,raw_data):
        current_offset = self.first_packet_offset
        # if we have more bytes than the initial header
        if len(raw_data) > self.first_packet_offset:
            while current_offset < len(raw_data):
                message_header = struct.unpack('>H',raw_data[current_offset:current_offset+2])[0]
                current_offset=current_offset+2
                #print "message header:" + hex(message_header)
                # Assert that the packet_type is 0x55aa
                if (message_header != 0x55aa):
                    #print "Have to skip and keep looking as this header is wrong"
                    continue
                message_type = struct.unpack('B',raw_data[current_offset:current_offset+1])[0]
                #print "message type:" + hex(message_type)
                current_offset=current_offset+1
                
                message_length = struct.unpack('B',raw_data[current_offset:current_offset+1])[0]
                #print "message length:" + hex(message_length)
                current_offset=current_offset+1
    
                # Next header check... current+length+checksum
                next_offset = current_offset+message_length+2
                if (next_offset+2) >= len(raw_data):
                    break
                next_header = struct.unpack('>h',raw_data[next_offset:next_offset+2])[0]
    
                # Check all the params before moving on...
                if (next_header != 0x55aa):
                    #print "Message must be wrong length..."
                    continue
    
                if message_type == 0x10:
                    xor_mask = struct.unpack('B',raw_data[current_offset+55:current_offset+56])[0]
                    #print "xor = " + str(xor_mask)
    
                    #BYTE 5-8 (DT): date and time, see details below
                    temp_data = self.decode_mask(raw_data[current_offset:current_offset+4],xor_mask)
                    time = struct.unpack('>l',temp_data)[0]
                    second = time & 0b00111111
                    time >>= 6
                    minute = time & 0b00111111
                    time >>= 6
                    hour = time & 0b00001111
                    if self.morning_night:
                        hour = hour + 16
                    time >>= 4
                    day = time & 0b00011111
                    time >>= 5
                    if (hour > 7):
                        day=day+1
                    month = time & 0b00001111
                    time >>= 4
                    year = time & 0b01111111
                    year = year + 2000
                    try:
                        dt = datetime(year, month, day, hour, minute, second)
                        #print dt
                    except:
                        #print "ERROR WITH TIME: %d %d %d %d %d %d" % (year, month, day, hour, minute, second) 
                        continue
    
                    current_offset=current_offset+4
    
                    # BYTE 9-12 (LO): longitude (x10^7, degree decimal)
                    temp_data = self.decode_mask(raw_data[current_offset:current_offset+4],xor_mask)
                    #print ''.join('{:02x}'.format(x) for x in temp_data)
                    longitude = float(struct.unpack('>l',temp_data)[0])/10000000.0
                    #print type(longitude)
                    current_offset=current_offset+4
                    #BYTE 13-16 (LA): latitude (x10^7, degree decimal)
                    temp_data = self.decode_mask(raw_data[current_offset:current_offset+4],xor_mask)
                    #print ''.join('{:02x}'.format(x) for x in temp_data)
                    latitude = float(struct.unpack('>l',temp_data)[0])/10000000.0
                    #print type(longitude)
                    current_offset=current_offset+4
                    #BYTE 17-20 (AL): altitude (in milimeters)
                    temp_data = self.decode_mask(raw_data[current_offset:current_offset+4],xor_mask)
                    altitude = float(struct.unpack('>l',temp_data)[0])/1000.0
                    current_offset=current_offset+4
                    #BYTE 21-24 (HA): horizontal accuracy estimate (see uBlox NAV-POSLLH message for details)
                    current_offset=current_offset+4
                    #BYTE 25-28 (VA): vertical accuracy estimate (see uBlox NAV-POSLLH message for details)
                    current_offset=current_offset+4
                    #BYTE 29-32: ??? (seems to be always 0)
                    current_offset=current_offset+4
                    #BYTE 33-36 (NV): NED north velocity (see uBlox NAV-VELNED message for details)
                    current_offset=current_offset+4
                    #BYTE 37-40 (EV): NED east velocity (see uBlox NAV-VELNED message for details)
                    current_offset=current_offset+4
                    #BYTE 41-44 (DV): NED down velocity (see uBlox NAV-VELNED message for details)
                    current_offset=current_offset+4
                    #BYTE 45-46 (PD): position DOP (see uBlox NAV-DOP message for details)
                    current_offset=current_offset+2
                    #BYTE 47-48 (VD): vertical DOP (see uBlox NAV-DOP message for details)
                    current_offset=current_offset+2
                    #BYTE 49-50 (ND): northing DOP (see uBlox NAV-DOP message for details)
                    current_offset=current_offset+2
                    #BYTE 51-52 (ED): easting DOP (see uBlox NAV-DOP message for details)
                    current_offset=current_offset+2
                    #BYTE 53 (NS): number of satellites (not XORed)
                    current_offset=current_offset+1
                    #BYTE 54: ??? (not XORed, seems to be always 0)
                    current_offset=current_offset+1
                    #BYTE 55 (FT): fix type (0 - no lock, 2 - 2D lock, 3 - 3D lock, 
                    #     not sure if other values can be expected - see uBlox NAV-SOL message for details)
                    current_offset=current_offset+1
                    #BYTE 56: ??? (seems to be always 0)
                    current_offset=current_offset+1
                    #BYTE 57 (SF): fix status flags (see uBlox NAV-SOL message for details)
                    current_offset=current_offset+1
                    #BYTE 58-59: ??? (seems to be always 0)
                    current_offset=current_offset+2
                    #BYTE 60 (XM): not sure yet, but I use it as the XOR mask
                    xor_mask = struct.unpack('>B',raw_data[current_offset:current_offset+1])[0]
                    current_offset=current_offset+1
                    #BYTE 61-62 (SN): sequence number (not XORed), once there is a lock - increases with every message. 
                    #     When the lock is lost later LSB and MSB are swapped with every message.
                    seq_num = struct.unpack('>H',self.decode_mask(raw_data[current_offset:current_offset+2],0x0))[0]
                    #print seq_num
                    current_offset=current_offset+2
                else:
                    current_offset=current_offset+message_length
    
                # Account for the checksum
                current_offset=current_offset+2
                
                if message_type == 0x10:
                    self.log.append(FlyTrexGPSData(dt,latitude,longitude,altitude*3.28084))
                    #print "GPS Data - " + str(longitude) + ' ' + str(latitude) + ' ' + str(altitude*3.28084) + 'f'
                
        

def main():
    myLog = FlyTrexLog(filename)
    myLog.writeCSV("foo")

if __name__=='__main__':
    main()
