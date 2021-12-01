# Used for testing the api and collecting data.

import requests
import json
import csv
from epa_api import epa_api

api = epa_api()

# NO, NO2, SO2, CO, CO2, PM10, PM2.5
chemicals = ["42605", "42602", "42401", "42101", "42102", "81102", "88101"]
times = ["05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00"]
date = "20200101"

def sites_to_csv():
    with open("data/listofEPAsites.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        header = ["STATE_CODE", "COUNTY_CODE", "COUNTY", "EPA ID", "SITE_LATITUDE", "SITE_LONGITUDE"]
        csv_writer.writerow(header)
        with open("siteCoordinates.json") as json_file:
            data = json.load(json_file)
            for d in data:
                row = list(d.values())
                csv_writer.writerow(row)
            json_file.close()
        csv_file.close()

def collect_site_coordinates():
    sites = api.sites_list()
    site_data = api.get_site_coordinates(sites, chemicals)
    print(*site_data, sep='\n')

    with open("siteCoordinates.json", "w") as file:
        json.dump(site_data, file, indent=2)
        file.close()

def test_api():
    sites = api.sites_list()
    for s in sites:
        county = s["county_code"]
        site = s["site_code"]
        print(api.get_data(county, site, date, date, times, chemicals))


test_api()
