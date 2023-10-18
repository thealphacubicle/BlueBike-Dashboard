"""
Supplemental code file for dashboard visualizations
DS3500 HW2
Authors: Reema Sharma
"""
import pandas as pd
import plotly.express as px
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
       Calculate the Haversine distance between two points on the Earth given their latitude and longitude.

       Args:
       - lat1, lon1: Latitude and longitude of the start point
       - lat2, lon2: Latitude and longitude of the end point.

       Returns:
       - Distance between the two points in kilometers.
    """

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
    """
        Create a histogram with KDE plot based on distance distribution for different user types.

        Args:
        - df: DataFrame
        - user_type_col: User type (casual or member)
        - dist_col: Distance in km
        - return_fig: If True, returns the figure. Otherwise, displays the figure.

        Returns:
        - Plotly figure if return_fig is True, else None.
    """

    fig = px.histogram(df, x=dist_col, color=user_type_col, marginal="rug", title="Distance KDE Plot")
    fig.update_layout(xaxis_title="Distance (km)", yaxis_title="Density")

    if return_fig:
        return fig
    else:
        fig.show()


def ride_duration(df, start_col, end_col):
    """
        Calculate ride duration and add it as a column to the given DataFrame.

        Args:
        - df: DataFrame
        - start_col: Ride start time in timestamp format
        - end_col: Ride end time in timestamp format

        Returns:
        - Edited DataFrame with ride duration column
    """

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
    """
        Remove outliers from a DataFrame based on Z-scores.

        Args:
        - df: DataFrame
        - col_name: Column name from which outliers need to be removed
        - user_type_col: User type (casual or member)
        - z_threshold: Z-score threshold to determine outliers, given as 2 by default

        Returns:
        - df_no_outliers: DataFrame without outliers
        - outliers_count: Count of outliers for each user type
    """

    z_scores = (df[col_name] - df.groupby(user_type_col)[col_name].transform('mean'))\
               / df.groupby(user_type_col)[col_name].transform('std')

    # Create a Boolean column that determines whether the row contains an outlier or not
    df['is_outlier'] = (z_scores < -z_threshold) | (z_scores > z_threshold)

    # Count the number of outliers for each user type
    outliers_count = df.groupby(user_type_col)['is_outlier'].sum().reset_index()

    df_no_outliers = df[~df['is_outlier']].drop(columns=['is_outlier'])

    return df_no_outliers, outliers_count


def create_violin_plot(df, duration_col, user_type_col, return_fig=False):
    """
        Create a violin plot showing ride duration distribution separated by rider type.

        Args:
        - df: DataFrame
        - duration_col: Ride duration in minutes
        - user_type_col: User type (casual or member)
        - return_fig: If True, returns the figure. Otherwise, displays the figure.

        Returns:
        - Plotly figure if return_fig is True, else None.
    """
    # Remove outliers from the 'ride_duration_minutes' column
    df = remove_outliers(df, duration_col, user_type_col)[0]

    # Create the violin plot using Plotly Express
    fig = px.violin(df, x=user_type_col, y='ride_duration_minutes', color=user_type_col,
                    box=True, points="all", title='Violin Plot of Ride Duration by Rider Type',
                    labels={'ride_duration_minutes': 'Duration (minutes)'},
                    category_orders={user_type_col: ['member', 'casual']})

    # Customize the plot
    fig.update_traces(meanline_visible=True)
    fig.update_layout(xaxis_title='Rider Type', yaxis_title='Duration (minutes)')

    if return_fig:
        return fig
    else:
        fig.show()


def time_series_plot(df, datetime_col, duration_col, user_type_col, member_val, casual_val, return_fig=False):
    """
    Creates a time series plot for ride duration over time aggregated by day

    Args:
    - df: DataFrame
    - datetime_col: Contains datetime values
    - duration_col: Contains ride duration values (in minutes as a float)
    - user_type_col: User type (casual or member)
    - member_val: 'member' string indicating that user is a member
    - casual_val: 'casual' string indicating that user is casual user
    - return_fig: If True, return the Plotly figure; if False, display the figure.
    """
    # Create separate DataFrames for member and casual users
    member_df = df[df[user_type_col] == member_val]
    casual_df = df[df[user_type_col] == casual_val]

    # Group data by date and calculate the mean ride duration for each date
    df = df.groupby(df[datetime_col].dt.date)[duration_col].mean().reset_index()
    member_df = member_df.groupby(member_df[datetime_col].dt.date)[duration_col].mean().reset_index()
    casual_df = casual_df.groupby(casual_df[datetime_col].dt.date)[duration_col].mean().reset_index()

    # Create an interactive time series plot
    fig = px.line(df, x=datetime_col, y=duration_col, labels={'x': 'Date', 'y': 'Average Duration (minutes)'},
                  title='Ride Duration (Aggregated by Date) by Rider Type in 2023')

    # Add labels in the legend for member, casual, and all users data
    fig.add_scatter(x=member_df[datetime_col], y=member_df[duration_col], mode='lines+markers',
                    name='Members')
    fig.add_scatter(x=casual_df[datetime_col], y=casual_df[duration_col], mode='lines+markers',
                    name='Casual Users')
    fig.add_scatter(x=df[datetime_col], y=df[duration_col], mode='lines+markers',
                    name='All Users')

    # Remove the year from the x-axis labels
    fig.update_xaxes(
        tickformat='%m-%d',
    )

    if return_fig:
        return fig
    else:
        fig.show()


def main():
    # Read the CSV file into a dataframe
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
    create_dist_kde(df, 'member_casual', 'distance')

    # Creates side-by-side violin plots for ride duration for members vs casual users
    create_violin_plot(df, 'ride_duration_minutes', 'member_casual')

    # Generate a time series plot
    time_series_plot(df, 'started_at', 'ride_duration_minutes', 'member_casual', 'member', 'casual')

    grouped_outliers = remove_outliers(df, 'ride_duration_minutes', 'member_casual')[1]
    print('The below shows how many outliers were dropped for members and casual riders respectively:')
    print(grouped_outliers)

    # Save the edited DataFrame to a CSV file
    df.to_csv('bluebike_updated.csv', index=False)


main()
