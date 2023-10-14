import pandas as pd
import geopandas as gpd
import sankey_proto as sk
import sankey as rsk
from artists import group_by

def main():
    df = pd.read_csv("bluebike_trunc.csv")

    # Make a Sankey diagram to show most common trips between a start and an end point
    start_end_df = group_by(df, ['start_station_name', 'end_station_name'], threshold=100)
    print(start_end_df)
    sk.make_sankey(start_end_df, 'start_station_name', 'end_station_name', vals='Count', title_text='Start vs End Trips')

    # Read geojson file into a dataframe
    boston_map = gpd.read_file("boston_boundaries.geojson")





main()
