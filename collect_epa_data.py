# Used for testing the api and collecting data.

import requests
import json
from epa_api import epa_api

api = epa_api()

# no, no2, so2, co, co2, o3, pm2.5,
date = "20200101"
times = ["06:00", "07:00", "08:00", "09:00", "10:00"]
chemicals = ["44201"]
sites = api.sites_list()
for s in sites:
    county = s["county_code"]
    site = s["site_code"]
    print(*api.get_data(county, site, date, times, chemicals), sep='\n')

CA = "06"
CO2 = "42102"
NO2 = "42602"
SO2 = "42401"
CarbonPM10 = "82116"
