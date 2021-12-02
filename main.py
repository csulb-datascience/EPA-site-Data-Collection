from Intersection import Intersection
import csv
import os
import json
from datetime import datetime
from epa_api import epa_api

file_format = "epa_zipcode_intersection_radius_{}.json"


def get_zipcodes():
    with open("./data/listofZipcodes.csv", "r") as file:
        return [int(row[0]) for row in csv.reader(file)]


def get_epa_sites():
    with open("./data/listofEPAsites.csv", "r") as file:
        data = csv.DictReader(file)
        return list(data)


def get_epa_zipcode_intersection(radius):
    o = Intersection()
    zipcode_list = get_zipcodes()
    epa_site_list = get_epa_sites()

    for epa_site in epa_site_list:
        latitude, longitude = float(epa_site["SITE_LATITUDE"]), float(epa_site["SITE_LONGITUDE"])
        # print(latitude, longitude)

        zipcode_intersection = []
        for zip_code in zipcode_list:
            return_type, circle_area, zipcode_area, intersection_area = o.get_intersection_area(latitude, longitude, radius, zip_code)

            if return_type == 1 and intersection_area > 0:

                print("Intersection found !!!", zip_code)
                zipcode_intersection.append(
                    {
                        "zipcode": zip_code,
                        "circle_area": circle_area,
                        "zipcode_area": zipcode_area,
                        "intersection_area": intersection_area
                    })
        epa_site["zipcode_intersections"] = zipcode_intersection
        print("===================================================")

    file_name = file_format.format(radius)
    with open(os.path.join("./intersection_details", file_name), mode='w') as jsonfile:
        json.dump(epa_site_list, jsonfile)


times = ["05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00"]  # time range: 5:00 - 11:00 AM

chemical_code_dict = {
    "NO": "42605",
    "NO2": "42602",
    "SO2": "42401",
    "CO": "42101",
    "CO2": "42102",
    "O3": "44201",
    "PM10": "81102",
    "PM2.5": "88101"
}


def get_site_chemical_details(county_code, county, site_id, bdate, edate, epa_data):
    api = epa_api()

    response = api.get_data(county_code, site_id, bdate, edate, times, chemical_code_dict.values())
    for date, time_dict in response.items():
        for time, chemicals_dict in time_dict.items():
            epa_data.append({
                "Date": date,
                "Time": time,
                "County": county,
                "EPA_ID": site_id,
                "NO": chemicals_dict[chemical_code_dict["NO"]],
                "NO2": chemicals_dict[chemical_code_dict["NO2"]],
                "SO2": chemicals_dict[chemical_code_dict["SO2"]],
                "CO": chemicals_dict[chemical_code_dict["CO"]],
                "CO2": chemicals_dict[chemical_code_dict["CO2"]],
                "O3": chemicals_dict[chemical_code_dict["O3"]],
                "PM2.5": chemicals_dict[chemical_code_dict["PM2.5"]],
                "PM10": chemicals_dict[chemical_code_dict["PM10"]],
            })


def get_data(radius):
    file_name = file_format.format(radius)
    # check if intersection file exists
    file = os.path.join("./intersection_details", file_name)
    if not os.path.exists(file):
        get_epa_zipcode_intersection(radius)

    with open(file) as f:
        epa_zipcode_intersection_list = json.load(f)

        epa_zipcode_data = []

        for epa_zipcode_intersection in epa_zipcode_intersection_list:
            # print(epa_zipcode_intersection)

            county_code = epa_zipcode_intersection["COUNTY_CODE"]
            county = epa_zipcode_intersection["COUNTY"]
            site_id = epa_zipcode_intersection["EPA_ID"]

            epa_data = []
            # date range: 01/01/2020 to present
            current_year = datetime.today().year
            while current_year >= 2020:
                bdate, edate = str(current_year)+"0101", str(current_year)+"1231"
                get_site_chemical_details(county_code, county, site_id, bdate, edate, epa_data)
                current_year -= 1

            print("County:", county, "site_id:", site_id, "epa_data len:", len(epa_data), "zipcode count:", len(epa_zipcode_intersection["zipcode_intersections"]))

            for zipcode_intersection in epa_zipcode_intersection["zipcode_intersections"]:

                for data in epa_data:
                    c = {key: value for (key, value) in (data.items() | zipcode_intersection.items())}
                    epa_zipcode_data.append(c)

        with open(f'./result/epa_zipcode_intersection_radius_{radius}_details.csv', 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Time', 'County', 'EPA_ID', 'zipcode', 'zipcode_area', 'circle_area', 'intersection_area', 'NO', 'NO2', 'SO2', 'CO', 'CO2', 'O3', 'PM2.5', 'PM10']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for d in epa_zipcode_data:
                writer.writerow(d)


if __name__ == '__main__':
    get_data(5)
