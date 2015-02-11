#!/usr/bin/env python

import json
import os
import csv
import copy
from datetime import datetime

# order the points by time

class FlightLog(object):

    def __init__(self, points):
        self.type = "FeatureCollection"
        self.features = []
        self.add_points(points)

    def add_points(self, points):
        for p in points:
            feature = Feature()
            feature.geometry.coordinates = [p.longitude, p.latitude, p.altitude]
            feature.properties = p
            self.features.append(feature)

    def write(self, filename='STDOUT'):

        output_directory = os.getcwd() # local working directory

        if filename.lower().endswith('.csv'):
            csvfile  = open(os.path.join(output_directory,filename), "wb")
            writer = csv.writer(csvfile, delimiter=',')
            header = ['id','time','latitude','longitude','elevation']
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
                writer.writerow(row)
                idcounter=idcounter+1
            csvfile.flush()
            csvfile.close()

        elif filename.lower().endswith('.json'):
            # write all data to geojson
            jsonfile = open(os.path.join(output_directory,filename), "wb")
            tmp = copy.deepcopy(self)
            for x in tmp.features:
                # update records with a string representation of timestamp
                strdate = x.properties.date.strftime('%Y-%m-%d %H:%M:%S')
                x.properties.date = strdate
            json.dump(tmp, jsonfile, default=lambda o: o.__dict__)
            del tmp

        elif filename == 'STDOUT':
            header = ['id','time','latitude','longitude','elevation']
            print ','.join(header)
            idcounter = 0
            for x in self.features:
                row = []
                row.append(idcounter)
                row.append(x.properties.date)
                row.append(x.properties.latitude)
                row.append(x.properties.longitude)
                row.append(x.properties.altitude)
                print ','.join(map(str, row))
                idcounter=idcounter+1

    def add_images(self, matches):
        # this function will add matched images to corresponding
        # points in the data structure.
        pass


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
