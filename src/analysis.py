import pandas as pd
import geopandas as gpd
import sankey_proto as sk
import sankey as rsk
from artists import group_by
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    earth_radius = 6371

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = earth_radius * c

    return distance


def create_dist_kde(df, user_type_col, dist_col):
    fig = px.histogram(df, x=dist_col, color=user_type_col, marginal="rug", title="Distance KDE Plot")
    fig.update_layout(xaxis_title="Distance (km)", yaxis_title="Density")
    fig.show()


def main():
    df = pd.read_csv("bluebike_trunc.csv")

    # Make a Sankey diagram to show most common trips between a start and an end point
    start_end_df = group_by(df, ['start_station_name', 'end_station_name'], threshold=100)
    # print(start_end_df)
    # sk.make_sankey(start_end_df, 'start_station_name', 'end_station_name', vals='Count', title_text='Start vs End Trips')
    # rsk.make_sankey(df, ['member_casual', 'start_station_name', 'end_station_name'], vals='Count', threshold=200)

    # Read geojson file into a dataframe
    boston_map = gpd.read_file("boston_boundaries.geojson")

    df['distance'] = df.apply(lambda row: haversine_distance(row['start_lat'], row['start_lng'],
                                                             row['end_lat'], row['end_lng']), axis=1)
    df = df[df['distance'] != 0]

    # Plot two Plotly KDE plots for distance travelled for members vs casual users
    create_dist_kde(df, 'member_casual', 'distance')

main()
