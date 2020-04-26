#!/usr/bin/env python

"""
The goal of this script is to parser a file with human-like addresses
and add the according geocode info (latitude and longitude)

CSV file example :

    ID, NUMBER, STREET
    01000002,   215,    rue de la Commune Ouest  (MTL)
    01000003,   1015,   rue Saint-Alexandre  (MTL)
    01000004,   221,    rue de la Commune Ouest  (MTL)

Example call::

    $ ./aggGeo.py path_to_csv_file

After processing the CSV file, the output is written down to path_to_csv_file.geo/

"""
import argparse
import logging
import sys

import datetime
from geopy.geocoders import Nominatim

import csv
import time

parser = argparse.ArgumentParser(usage="%(prog)s [options]\n" + __doc__)
parser.add_argument('csv_file_path',
                    metavar='PATH',
                    help='Path to the csv file')
parser.add_argument('-l', '--log-file',
                    help='Specify the log file.')

LOGGING_FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'

class Geo():
    def __init__(self,options):
        self.options = options
        self.file_path = self.options.csv_file_path
        self.geolocator = Nominatim(user_agent="capstone-project-11")
    
    
    def getGeocode(self, address):
        try: 
            location = self.geolocator.geocode(address)
            lat = location.latitude
            lng = location.longitude
                
        except:
            logging.error('Unable to get geocode for %s' %address)
            lat = 'n/a'
            lng = 'n/a'
        
        return (lat,lng)
    
    def process_file(self):
        file_to_process = self.file_path
        new_file = file_to_process + '.geo'
        
        fields = ['NUMBER','STREET','STREET_NO_REGION','LATITUDE','LONGITUDE']

        with open(file_to_process, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            
            i = 1
            for row in reader:

                if i == 1:
                    with open(new_file, 'w') as outfile:
                        writer = csv.DictWriter(outfile, fields)
                        writer.writeheader()

                if (i%100 == 0) or (i<10):
                    logging.info("Handling %d record" %i) #log just first 10 and every 100 loops

                if 'LATITUDE' not in row or row['LATITUDE'] == 'n/a':
                    
                    streetNumber = row['NUMBER']
                    streetName = row['STREET_NO_REGION']

                    address = streetNumber + ' ' + streetName + ' Montreal'

                    logging.info("Updating %d record" %i)
                    location = self.getGeocode(address)

                    row['LATITUDE'] = location[0]
                    row['LONGITUDE'] = location[1]

                    time.sleep(1.1)
                
                with open(new_file, 'a', newline='') as outfile:
                    writer = csv.DictWriter(outfile, row.keys())
                    writer.writerow(row)                

                i+=1

if __name__ == '__main__':
    options = parser.parse_args()
    if options.log_file:
        logging.basicConfig(filename=options.log_file, format=LOGGING_FORMAT, level=logging.INFO)
        
    
    g1 = Geo(options)
    g1.process_file()

    logging.info("Done")
    