#!/usr/bin/env python

import json
import os
import csv
import copy
from datetime import datetime

# order the points by time

# Generic FLightLog class to hold just points with a minimum number of attributes:
# i.e. Time, Lat, Lon, Altitude
# It can also hold arbitrary properties in addition to the minimal required attributes. 
class FlightLog(object):

    def __init__(self, points=None):
        self.type = "FeatureCollection"
        self.features = []
        if points:
            self.add_points(points)

            
    def add_point(self, point):
        feature = Feature()
        feature.geometry.coordinates = [point.longitude, point.latitude, point.altitude]
        feature.properties = point
        self.features.append(feature)
        return feature

    def add_points(self, points):
        for p in points:
            self.add_point(p)

    def write(self, filename='STDOUT'):

        output_directory = os.getcwd() # local working directory

        if filename.lower().endswith('.csv') and len(self.features)>0:
            csvfile  = open(os.path.join(output_directory,filename), "wb")
            writer = csv.writer(csvfile, delimiter=',')
            header = ['id','time','latitude','longitude','elevation']
            # Add in the image filename if it is there
            if hasattr(self.features[0].properties, 'image'):
                header.extend(['image'])
            # add extra headers if needed
            #header.extend(extra)
            writer.writerow(header)
            idcounter = 0
            for x in self.features:
                row = []
                # add extra data if extra headers where used
                # row.extend(extra_out)
                row.append(str(idcounter))
                row.append(x.properties.date)
                row.append(x.properties.latitude)
                row.append(x.properties.longitude)
                row.append(x.properties.altitude)
                if hasattr(x.properties, 'image'):
                    row.append(x.properties.image)
                writer.writerow(row)
                idcounter=idcounter+1
            csvfile.flush()
            csvfile.close()

        elif filename.lower().endswith('.json') and len(self.features)>0:
            # write all data to geojson
            jsonfile = open(os.path.join(output_directory,filename), "wb")
            tmp = copy.deepcopy(self)
            #print tmp
            for x in tmp.features:
                #print x.properties.date
                # update records with a string representation of timestamp
                strdate = x.properties.date.strftime('%Y-%m-%d %H:%M:%S')
                x.properties.date = strdate
            json.dump(tmp, jsonfile, default=lambda o: o.__dict__)
            del tmp

        elif filename == 'STDOUT' and len(self.features)>0:
            header = ['id','time','latitude','longitude','elevation']
            # Add in the image filename if it is there
            if hasattr(self.features[0].properties, 'image'):
                header.extend(['image'])
            print ','.join(header)
            idcounter = 0
            for x in self.features:
                row = []
                row.append(idcounter)
                row.append(x.properties.date)
                row.append(x.properties.latitude)
                row.append(x.properties.longitude)
                row.append(x.properties.altitude)
                if hasattr(x.properties, 'image'):
                    row.append(x.properties.image)
                print ','.join(map(str, row))
                idcounter=idcounter+1

    def add_images(self, matches):
        # this function will add matched images to corresponding
        # points in the data structure.
        pass


class FlightSyncLog(FlightLog):
    def __init__(self):
        super(FlightSyncLog, self).__init__()

    def add_image(self, image, log, offset=0):

        # Find the image date
	import exifread
	from datetime import datetime, timedelta
	f = open(image, 'rb')
	tags = exifread.process_file(f)
	f.close()
	exifDateStr = tags['EXIF DateTimeDigitized'].values
	exifDate = datetime.strptime(exifDateStr, "%Y:%m:%d %H:%M:%S")

        # Apply offset to the datetime
        searchDate = exifDate + timedelta(seconds=int(offset))

        # Need to properly deal with timezone... but for now assume we add 8 hours to get to UTC
        searchDate = searchDate + timedelta(hours=8)

        # Need to loop through the log and find the closest point
        diff = timedelta(seconds=999999)
        closest = None
        #print len(log.features)
        for x in log.features:
            calcdiff = searchDate - x.properties.date
            #print calcdiff
            if abs(calcdiff) < diff:
                # we have a winner... the best so far
                closest = x
                diff = abs(calcdiff)
        
        # Now we have the feature that is the closest... we add to our internal log
        newPoint = self.add_point(closest.properties)
        # Add the image ref into the feature
        newPoint.properties.image = image


class Feature(object):
    def __init__(self):
        self.type = "Feature"
        self.properties = Store()
        self.geometry = Store()
        self.geometry.type = "Point"
        self.geometry.coordinates = []


class Store(object):
    def __init__(self):
        pass
