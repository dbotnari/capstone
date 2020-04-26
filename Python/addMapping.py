#!/usr/bin/env python

"""
The goal of this script is to parse a file with geocode info (latitude and longitude)
and map each record with the appropriate geographical unit

CSV file example :

    ..., LATITUDE, LONGITUDE, ...
    ...,   45.5019987,-73.553966, ...
    ...,   45.5030523,-73.562862, ...
    ...,   45.5019322,-73.5539692, ...

Example call::

    $ ./addMapping.py path_to_csv_file

After processing the CSV file, the output is written down to path_to_csv_file.map/

"""
import argparse
import logging
import sys

import datetime
import csv

import numpy as np

parser = argparse.ArgumentParser(usage="%(prog)s [options]\n" + __doc__)
parser.add_argument('csv_file_path',
                    metavar='PATH',
                    help='Path to the csv file')
parser.add_argument('-l', '--log-file',
                    help='Specify the log file.')

LOGGING_FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
#Montreal extreme points
LAT_MIN = 45.4
LNG_MIN = -74.0
LAT_MAX = 45.71
LNG_MAX = -73.47

NB_BINS = 100 # finally, the grid will have NB_BINS x NB_BINS  geographical units
#LAT_DELTA = 0.0031 = 0.34km
#LNG_DELTA = 0.0053 = 0.41km

class Map():
    def __init__(self,options):
        self.options = options
        self.file_path = self.options.csv_file_path
        self.lat_bins = np.linspace(LAT_MIN, LAT_MAX, num=NB_BINS+1)
        self.lng_bins = np.linspace(LNG_MIN, LNG_MAX, num=NB_BINS+1)
        self.__define_grid()
    
    def __define_grid(self):
        grid = []       
        for j in range(1,101):
            for i in range(1,101):
                row = {}
                row['ID'] = str(i) + '-' + str(j)
                row['LAT_MIN'] = self.lat_bins[i-1]
                row['LNG_MIN'] = self.lng_bins[j-1]
                row['LAT_MAX'] = self.lat_bins[i]
                row['LNG_MAX'] = self.lng_bins[j]
                row['LAT_ID'] = i
                row['LNG_ID'] = j
                grid.append(row)
        
        self.grid = grid

    def get_gridID(self, latitude, longitude):
        lat_map = np.digitize(latitude,self.lat_bins)
        lng_map = np.digitize(longitude,self.lng_bins)
        
        try: 
            id_map = list(filter(lambda item: item['LAT_ID'] == lat_map and item["LNG_ID"] == lng_map, self.grid))[0]['ID']
            return id_map
        except:
            logging.error("Wrong coordinates: %f %f" % (latitude, longitude))

    def export_grid(self):
        grid_file = 'grid.csv'
        
        with open(grid_file, 'w') as outfile:
            rows = self.grid
            writer = csv.DictWriter(outfile, rows[0].keys())
            writer.writeheader()
            for row in rows:
                    writer.writerow(row)

    def process_file(self):
        file_to_process = self.file_path
        new_file = file_to_process + '.map'
        

        with open(file_to_process, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            rows = []
            i = 1
            for row in reader:
                if (i%100 == 0) or (i<10):
                    logging.info("Handling %d record" %i) #log just first 10 and every 100 loops
                
                latitude = float(row['LATITUDE'])
                longitude = float(row['LONGITUDE'])
                
                row['MAP_ID'] = self.get_gridID(latitude, longitude)

                rows.append(row)
                i+=1
         
        with open(new_file, 'w', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, rows[0].keys())
            writer.writeheader()
            for row in rows:
                    writer.writerow(row)

if __name__ == '__main__':
    options = parser.parse_args()
    if options.log_file:
        logging.basicConfig(filename=options.log_file, format=LOGGING_FORMAT, level=logging.INFO)
        
    
    g1 = Map(options)
    g1.process_file()
    g1.export_grid()

    logging.info("Done")