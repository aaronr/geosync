geosync
=======

Geosync photos to GPS logs (like from a Flytrex data logger).

## The problem.

You've got a ton of images from your UAV (you have one, right?) without proper `EXIF` geo data.. **darn!** Your only hope is to interpolate image's timestamp with the GPS timestamp. Your UAV's GPS  data are typically mashed into binary, which makes reading it impossible without some online tools or proprietary software.

## The solution.

Geosync! This CLI tool does a few things in one fell swoop.

1. Crunches through the binary file, of which your data type (manufacturer specific) is defined in the CLI (currently only `flytrex` works), to output a nicely formatted CSV file with the proper geodata and timestamp of your UAV's GPS info.
1. Image time offset (`--offsetcalc`) calculates the offset between the camera clock and the GPS time (UTC) to ensure your timestamps are matching and *step 3* interpolates with the proper offset.
1. Scrapes the EXIF data from your images. For each image, `geosync.py` interpolates a lat/lng pair by comparing the image's timestamp with the GPS timestamps and setting the proper offset from *step 2*.
1. Properly formatted lat/lng values are returned with the image's filename into a new, useable CSV to use when building.

## Usage. `./geosync` (currently a wishlist!)

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

EXAMPLES:

# Read a flytrex file and write out the results to a file
./geosync.py --flytrex --flyout test.csv test/00000004.FPV

# Read a flytrex file and write the results to stdout
./geosync.py --flytrex test/00000004.FPV

# Calculate the time offset for a single file
./geosync.py --offsetcalc "2014-12-17 13:02:00" test/IMG_1993.JPG

# Geosync with a single image against a flytrex file... output to stdout
./geosync.py --geotag --offset 10 --geolog flytrex test/00000005.FPV test/IMG_0935.JPG

# Geosync with output to .json
./geosync.py --geotag --geoout tst.json --offset 10 --geolog flytrex test/00000005.FPV test/IMG_0935.JPG

# Geosync with a glob filename input
./geosync.py --geotag --geoout test.geojson --offset 10 --geolog flytrex test/00000005.FPV test/*.JPG

# pretty-print the json output
python -m json.tool test.geojson
