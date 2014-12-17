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
                                    ">>> geosync --flytrex [--flyout (CSV|GEOJSON)] logfile [outfile]")
        flytrex_group.add_option("--flytrex", 
                                 action="store_true", dest="flytrex", default=False,
                                 help="FlyTrex Logfile Processing.")
        flytrex_group.add_option("--flyout", 
                                 dest="format",
                                 help="Output Format. Options STDOUT|CSV|GEOJSON. [STDOUT]")
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
                               ">>> geosync --geotag [--geoout (EXIF|CSV|GEOJSON)] [--offset offset] logfile (imagefile|directory) [outfile]")
    geotag_group.add_option("--geotag", 
                            action="store_true", dest="geotag", default=False,
                            help="Geotag photo(s) from GPS logfile")
    geotag_group.add_option("--geoout", 
                            dest="format",
                            help="Output Format. Options EXIF|CSV|GEOJSON. [STDOUT]")
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
        myLog.writeCSV("foo")
