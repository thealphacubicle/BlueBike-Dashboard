import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import math
from matplotlib.dates import DayLocator
from datetime import datetime



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


def create_dist_kde(df, user_type_col, dist_col, return_fig=False):
    fig = px.histogram(df, x=dist_col, color=user_type_col, marginal="rug", title="Distance KDE Plot")
    fig.update_layout(xaxis_title="Distance (km)", yaxis_title="Density")

    if return_fig:
        return fig
    else:
        fig.show()


def ride_duration(df, start_col, end_col):
    # Convert timestamp columns to datetime
    df[start_col] = pd.to_datetime(df[start_col])
    df[end_col] = pd.to_datetime(df[end_col])

    # Calculate time elapsed
    df['ride_duration'] = df[end_col] - df[start_col]

    # Drop rows in the 'distance' column if 'ride_duration' is 0
    df = df[df['ride_duration'] != 0]

    # Create a column to store only the minutes and seconds
    df['ride_duration_minutes'] = df['ride_duration'].dt.total_seconds() / 60

    # Drop rows with time elapsed of 0
    df = df[df['ride_duration_minutes'] != pd.Timedelta(0)]
    df = df.drop(columns='ride_duration')

    return df


def remove_outliers(df, col_name, user_type_col, z_threshold=2):
    z_scores = (df[col_name] - df.groupby(user_type_col)[col_name].transform('mean'))\
               / df.groupby(user_type_col)[col_name].transform('std')

    # Create a Boolean column that determines whether the row contains an outlier or not
    df['is_outlier'] = (z_scores < -z_threshold) | (z_scores > z_threshold)

    # Count the number of outliers for each user type
    outliers_count = df.groupby(user_type_col)['is_outlier'].sum().reset_index()

    df_no_outliers = df[~df['is_outlier']].drop(columns=['is_outlier'])

    return df_no_outliers, outliers_count


def create_violin_plot(df, duration_col, rider_type_col, return_fig=False):
    # Remove outliers from the 'ride_duration_minutes' column
    df = remove_outliers(df, duration_col, rider_type_col)[0]

    # Create the violin plot using Plotly Express
    fig = px.violin(df, x=rider_type_col, y='ride_duration_minutes', color=rider_type_col,
                    box=True, points="all", title='Violin Plot of Ride Duration by Rider Type',
                    labels={'ride_duration_minutes': 'Duration (minutes)'},
                    category_orders={rider_type_col: ['member', 'casual']})

    # Customize the plot
    fig.update_traces(meanline_visible=True)
    fig.update_layout(xaxis_title='Rider Type', yaxis_title='Duration (minutes)')

    if return_fig:
        return fig
    else:
        fig.show()


def time_series_plot(df, datetime_col, duration_col, member_col, member_val, casual_val, return_fig=False):
    """
    Create a time series plot for ride duration over time.

    Parameters:
    - df: DataFrame
    - datetime_col: Contains datetime values
    - duration_col: Contains ride duration values (in minutes as a float)
    - member_col: Indicates whether the rider is a member or casual user
    - member_val: 'member' string indicating that user is a member
    - casual_val: 'casual' string indicating that user is casual user
    - return_fig: If True, return the Plotly figure; if False, display the figure.
    """
    # Create separate DataFrames for member and casual users
    member_df = df[df[member_col] == member_val]
    casual_df = df[df[member_col] == casual_val]

    # Group data by date and calculate the mean duration for each date
    df = df.groupby(df[datetime_col].dt.date)[duration_col].mean().reset_index()
    member_df = member_df.groupby(member_df[datetime_col].dt.date)[duration_col].mean().reset_index()
    casual_df = casual_df.groupby(casual_df[datetime_col].dt.date)[duration_col].mean().reset_index()

    # Create an interactive time series plot using Plotly
    fig = px.line(df, x=datetime_col, y=duration_col, labels={'x': 'Date', 'y': 'Average Duration (minutes)'},
                  title='Ride Duration (Aggregated by Date) by Rider Type in 2023')

    # Add traces for member and casual data
    fig.add_scatter(x=member_df[datetime_col], y=member_df[duration_col], mode='lines+markers',
                    name='Members')
    fig.add_scatter(x=casual_df[datetime_col], y=casual_df[duration_col], mode='lines+markers',
                    name='Casual Users')
    fig.add_scatter(x=df[datetime_col], y=df[duration_col], mode='lines+markers',
                    name='All Users')

    # Remove the year from the x-axis labels
    fig.update_xaxes(
        tickformat='%m-%d',  # Customize the date format here (month and day only)
    )

    if return_fig:
        return fig
    else:
        fig.show()




def main():
    df = pd.read_csv("bluebike_trunc.csv")

    # Drop unnecessary columns
    df.drop(['ride_id', 'start_station_id', 'end_station_id'], axis=1, inplace=True)
    df = df.dropna()

    # Create distance column
    df['distance'] = df.apply(lambda row: haversine_distance(row['start_lat'], row['start_lng'],
                                                             row['end_lat'], row['end_lng']), axis=1)


    # Convert to datetime format to find the time elapsed during rides
    df = ride_duration(df, 'started_at', 'ended_at')

    # Plot overlapping Plotly KDE plots for distance travelled for members vs casual users
    #create_dist_kde(df, 'member_casual', 'distance')

    # create_violin_plot(df, 'ride_duration_minutes', 'member_casual')

    # Generate the time series plot
    #time_series_plot(df, 'started_at', 'ride_duration_minutes', 'member_casual', 'member', 'casual')

    grouped_outliers = remove_outliers(df, 'ride_duration_minutes', 'member_casual')[1]
    # print(grouped_outliers)

    # Save the DataFrame to a CSV file
    df.to_csv('bluebike_updated.csv', index=False)

main()
