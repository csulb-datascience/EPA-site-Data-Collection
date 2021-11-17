import requests
import json

class epa_api:
    # Use EPA API to retrieve list of different categories of chemicals measured by EPA
    def get_chemical_classes(self):
        response = requests.get("https://aqs.epa.gov/data/api/list/classes?email=david.eaton@student.csulb.edu&key=orangeswift34")
        with open("chemicals/chemical_classes.json", "w") as file:
            file.write(response.text)
            file.close()

    # Parse JSON file retrieved from EPA API to generate dictionary of class names and descriptions.
    def chem_classes_dict(self):
        result = {}
        with open("chemicals/chemical_classes.json") as json_file:
            data = json.load(json_file)
            for chemical in data["Data"]:
                result[chemical["code"]] = chemical["value_represented"]
        return result

    # Use EPA API to retrieve lists of all chemicals measured for each class
    def get_chemicals(self):
        chemical_classes = self.chem_classes_dict()
        for chemical_class in chemical_classes:
            response = requests.get(f"https://aqs.epa.gov/data/api/list/parametersByClass?email=david.eaton@student.csulb.edu&key=orangeswift34&pc={chemical_class}")
            file_name = f"chemicals/chemicals_{chemical_class.replace(' ', '_').replace('.', '').replace('/', '')}.json"
            with open(file_name, "w") as file:
                file.write(response.text)
                file.close()

    # Use EPA API to retrieve list of states and state codes.
    def get_states(self):
        response = requests.get("https://aqs.epa.gov/data/api/list/states?email=david.eaton@student.csulb.edu&key=orangeswift34")
        with open("states.json", "w") as file:
            file.write(response.text)
            file.close()

    # Parse JSON file retrieved from EPA to generate a dictionary of states and their codes
    def states_dict(self):
        result = {}
        with open("states.json") as json_file:
            data = json.load(json_file)
            for state in data["Data"]:
                result[state["value_represented"]] = state["code"]
        return result

    # Use EPA API to retrieve list of all counties for the state of CA
    def get_counties(self):
        response = requests.get("https://aqs.epa.gov/data/api/list/countiesByState?email=david.eaton@student.csulb.edu&key=orangeswift34&state=06")
        with open("counties.json", "w") as file:
            file.write(response.text)
            file.close()

    # Parse JSON file retrieved from EPA to generate a dictionary of CA counties and their county code.
    def counties_dict(self):
        result = {}
        with open("counties.json") as json_file:
            data = json.load(json_file)
            for county in data["Data"]:
                result[county["value_represented"]] = county["code"]
        return result

    # Use EPA API to retrieve lists of all the sites in each CA county.
    def get_sites(self):
        counties = self.counties_dict()
        for county in counties:
            response = requests.get(f"https://aqs.epa.gov/data/api/list/sitesByCounty?email=david.eaton@student.csulb.edu&key=orangeswift34&state=06&county={counties[county]}")
            file_name = f"sites/sites_{county.replace(' ', '_')}.json"
            with open(file_name, "w") as file:
                file.write(response.text)
                file.close()

    # Parse JSON retrieved from EPA to create a list of all sites.
    # Each site is represented in the list as its own dictionary
    def sites_list(self):
        result = []
        counties = self.counties_dict()
        for county in counties:
            file_name = f"sites/sites_{county.replace(' ', '_')}.json"
            with open(file_name) as json_file:
                data = json.load(json_file)
                for site in data["Data"]:
                    site_info = {
                        "county": county,
                        "county_code": counties[county],
                        "site_name": site["value_represented"],
                        "site_code": site["code"]
                    }
                    result.append(site_info)
        return result

    def get_data(self, county, site, date, times, chemicals):
        result = []
        chemicals_list = ",".join(chemicals)
        response = requests.get(f"https://aqs.epa.gov/data/api/sampleData/bySite?email=david.eaton@student.csulb.edu&key=orangeswift34&param={chemicals_list}&bdate={date}&edate={date}&state=06&county={county}&site={site}")
        raw_data = json.loads(response.text)
        print(raw_data["Header"])
        for reading in raw_data["Data"]:
            if reading["time_local"] in times:
                result.append(reading)
        return result

    def get_site_coordinates(self, sites, chemicals):
        result = []
        for s in sites:
            county = s["county_code"]
            site = s["site_code"]
            for c in chemicals:
                response = requests.get(f"https://aqs.epa.gov/data/api/sampleData/bySite?email=david.eaton@student.csulb.edu&key=orangeswift34&param={c}&bdate=20200101&edate=20201231&state=06&county={county}&site={site}")
                raw_data = json.loads(response.text)
                for reading in raw_data["Data"]:
                    site_info = {
                        "state_code": reading["state_code"],
                        "county_code": reading["county_code"],
                        "county": reading["county"],
                        "site_number": reading["site_number"],
                        "latitude": reading["latitude"],
                        "longitude": reading["longitude"]
                    }
                    if not any(r["county_code"] == site_info["county_code"] and r["site_number"] == site_info["site_number"] for r in result):
                        result.append(site_info)
        return result
