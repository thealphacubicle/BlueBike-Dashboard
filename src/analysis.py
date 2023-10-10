"""
Does the data cleaning and data preperation for the dashboard
DS3500 HW2
Authors: Srihari Raman & Reema Sharma
"""

import pandas as pd
import requests
from pprint import pprint
import time
import os
from dotenv import load_dotenv

# API credentials
load_dotenv("keys.env")
API_KEY = os.getenv('API_KEY')

# Clean dataset
df = pd.read_csv("https://raw.githubusercontent.com/thealphacubicle/MBTA-Dashboard/main/src/data/mbta_cr_data.csv")
#print(df.isna().sum())
df = df.dropna()

# print("\nPost-processing data shape:" ,df.shape)

# Collect geolocation data using OpenWeather API for map plot
def get_lat_long(city, state="Massachusetts", country="US", key=API_KEY):
    """
    Gets the latitude and longitude using OpenWeather API's forward geolocation API.
    :param city: City name
    :param state: State name
    :param country: Country name
    :param key: API key for OpenWeather API Geolocation
    :return: Tuple of (latitude, longitude)
    """

    res = requests.get(url=f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}"
                           f"&limit={2}&appid={key}").json()[0]

    return res['lat'], res['lon']


# Store latitude and longitude details for available route stops in the dataframe
locations = {}
for city in df['stop_id'].unique():
    try:
        locations[city] = get_lat_long(city)
    except Exception as e:
        # print(f"{city} got no lat/long results")
        pass

def get_coordinates(city_name):
    """
    Returns the coordinates of the city if found in the locations dictionary
    :param city_name: City name
    :return: Coordinates of the city
    """
    if city_name in locations.keys():
        return locations[city_name]
    else:
        return (-1,-1)

df['coordinates'] = df['stop_id'].apply(get_coordinates)
df.to_csv("./data/cleaned_data.csv")