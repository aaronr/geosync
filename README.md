geosync
=======

Geosync photos to GPS logs (like from a Flytrex data logger)

**Something like:**
    Usage: geosync.py [options]* arg1 [arg]*
    
    Options:
      -h, --help         show this help message and exit
      -v, --verbose      Verbose output
      -q, --quiet        Quiet output
      -d, --debug        Enable debug output
    
      FlyTrex Options:
        Set of command options specific to processing the FlyTrex data logs.
        >>> geosync --flytrex [--flyout (CSV|GEOJSON)] logfile [outfile]
    
        --flytrex        FlyTrex Logfile Processing.
        --flyout=FORMAT  Output Format. Options STDOUT|CSV|GEOJSON. [STDOUT]
    
      Image Time Offset Options:
        Set of command options specific to calculating offset between
        camera clock and GPS time (UTC). Defaults to STDOUT.
        NOTE: Timestring form "2014-10-25 17:01:05"
        >>> geosync --offsetcalc timestring imagefile [outfile]
    
        --offsetcalc     Camera time vs. GPS time offset processing
    
      GeoTag Image(s) Options:
        Set of command options specific to geotagging photos from GPS data.
        >>> geosync --geotag [--geoout (EXIF|CSV|GEOJSON)] [--offset offset]
        logfile (imagefile|directory) [outfile]
    
        --geotag         Geotag photo(s) from GPS logfile
        --geoout=FORMAT  Output Format. Options EXIF|CSV|GEOJSON. [STDOUT]
        --offset=OFFSET  Offset to apply between GPS time and camera time in
                         seconds. [0.0]
