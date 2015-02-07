#!/usr/bin/env python

# Process uav files in prep for processing.  This includes data logger and image 
# files used for stitching and SFM processing

available_libs = []
try:
    import flytrex
    available_libs.append("flytrex")
except:
    pass

import glob
import os
from optparse import OptionParser, OptionGroup
import logging
logger=logging.getLogger(__name__)
import re
import csv

class GeosyncLogRecord(object):
    def __init__(self, logid, filename):
        self.logid=logid
        self.filename=filename


class Geosync(object):
    log = []
    def __init__(self, logfile, offset, inputfiles):
        '''
        A Geosync object is the structure to hold the synced data
        '''
        # This is actually a "geosync" geojson file
        self.logfile = logfile
        # float indicating time offset
        self.offset = offset
        # list of files to sync up
        self.inputfiles = inputfiles
        
        # Try to do the sync
        # Itterate over input files
          # Read the exif time from file
          # apply offset if non-zero
          # Find the closest matching GPS record from logfile
          # Write the id<->filename mapping to internal store

    def write(self,outfile=None):
        # Itterate over our internal store
          # Lookup ID from logfile
          # write out record (i.e. filename, time, lat, lon, elevation, extras

        pass

if __name__ == '__main__':
    usage = "usage: %prog [options]* arg1 [arg]*"
    parser = OptionParser(usage=usage)

    # General
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Verbose output")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet", default=False,
                      help="Quiet output")
    parser.add_option("-d", "--debug", 
                      action="store_true", dest="debug", default=False,
                      help="Enable debug output")

    # Flytrex Specific Options
    if "flytrex" in available_libs:
        flytrex_group = OptionGroup(parser, "FlyTrex Options",
                                    "Set of command options specific to processing the FlyTrex data logs.\n"
                                    ">>> geosync --flytrex [--flyout (*.csv|*.geojson)] logfile")
        flytrex_group.add_option("--flytrex", 
                                 action="store_true", dest="flytrex", default=False,
                                 help="FlyTrex Logfile Processing. Dumps to stdout if no --flyout")
        flytrex_group.add_option("--flyout", 
                                 dest="flyout",
                                 help="Output File. Type based on file extenaion. Options csv|geojson")
        parser.add_option_group(flytrex_group)

    # Offset Options
    offsetcalc_group = OptionGroup(parser, "Image Time Offset Options",
                               "Set of command options specific to calculating offset between          "
                               "camera clock and GPS time (UTC). Defaults to STDOUT.                   "
                               "NOTE: Timestring form \"2014-10-25 17:01:05\"                          "
                               ">>> geosync --offsetcalc timestring imagefile [outfile]")
    offsetcalc_group.add_option("--offsetcalc", 
                            action="store_true", dest="offsetcalc", default=False,
                            help="Camera time vs. GPS time offset processing")
    parser.add_option_group(offsetcalc_group)
    
    # GeoTag Options
    geotag_group = OptionGroup(parser, "GeoTag Image(s) Options",
                               "Set of command options specific to geotagging photos from GPS data.    "
                               ">>> geosync --geotag [--geoout (*.csv|*.geojson)] [--offset offset] logfile (imagefile|directory)")
    geotag_group.add_option("--geotag", 
                            action="store_true", dest="geotag", default=False,
                            help="Geotag photo(s) from GPS logfile")
    geotag_group.add_option("--geoout", 
                            dest="geoout",
                            help="Output File. Type based on file extenaion. Options csv|geojson")
    geotag_group.add_option("--geolog", 
                            dest="geolog",
                            help="The logfile type being referenced (flytrex) [flytrex]")
    geotag_group.add_option("--offset", 
                            dest="offset",
                            help="Offset to apply between GPS time and camera time in seconds. [0.0]")
    parser.add_option_group(geotag_group)


    (options, args) = parser.parse_args()
    # Take care of logging
    if options.debug:
        level=logging.DEBUG
    else:
        level=logging.INFO
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)

    if options.flytrex and ("flytrex" in available_libs):
        myLog = flytrex.FlyTrexLog(args[0])
        if options.flyout:
            myLog.write(options.flyout)
        else:
            # Default to STDOUT
            myLog.write()
    elif options.offsetcalc:
	import exifread
	from datetime import datetime
	imgDate = datetime.strptime(args[0], "%Y-%m-%d %H:%M:%S")
	f = open(args[1], 'rb')
	tags = exifread.process_file(f)
	f.close()
	exifDateStr = tags['EXIF DateTimeDigitized'].values
	exifDate = datetime.strptime(exifDateStr, "%Y:%m:%d %H:%M:%S")
	diff = exifDate - imgDate
	print diff.total_seconds()
    elif options.geotag:
        # Lets pull it all together and geotag some photos
        myLog = None
        if options.geolog:
            if options.geolog == 'flytrex' and ("flytrex" in available_libs):
                # convert to geosync interchange format
                #myLog = flytrex.FlyTrexLog(args[0]).toGeoSync()
                myLog = flytrex.FlyTrexLog(args[0])

        # Sync stuff up
        files = args[1]
        offset = 0
        if options.offset:
            offset = options.offset
        mySyncLog = Geosync(myLog,offset,files)
        if options.geoout:
            # Need to write out the synced log to file
            mySyncLog.write(options.geoout)
        else:
            # Default to STDOUT
            mySyncLog.write()
        
