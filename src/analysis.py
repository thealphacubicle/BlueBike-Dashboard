import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import math
from matplotlib.dates import DayLocator


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


def ride_duration(df, start_col, end_col):
    # Convert timestamp columns to datetime
    df[start_col] = pd.to_datetime(df[start_col])
    df[end_col] = pd.to_datetime(df[end_col])

    # Calculate time elapsed
    df['ride_duration'] = df[end_col] - df[start_col]
    df['ride_duration_minutes'] = df['ride_duration'].dt.total_seconds() / 60

    # Drop rows with time elapsed of 0
    df = df[df['ride_duration_minutes'] != pd.Timedelta(0)]
    df = df.drop(columns='ride_duration')

    return df


def create_bubble_chart(df, dist_col, rider_type_col):
    # Remove outliers from the 'ride_duration_minutes' column
    df = remove_outliers(df, 'ride_duration_minutes')
    print(df['ride_duration_minutes'].max())

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Define colors for member and casual riders
    colors = {'member': 'blue', 'casual': 'red'}

    # Plot the bubbles
    for rider_type, group in df.groupby(rider_type_col):
        ax.scatter(group[dist_col], group['ride_duration_minutes'], c=colors[rider_type], label=rider_type, alpha=0.7, s=100)

    # Set axis labels and legend
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Duration (minutes)')
    ax.legend(title='Rider Type')

    # Customize the plot
    plt.title('Bubble Chart of Distance vs Duration by Rider Type')
    plt.grid(True)

    # Show the plot
    plt.show()


def remove_outliers(df, col_name, z_threshold=2):
    z_scores = (df[col_name] - df[col_name].mean()) / df[col_name].std()
    df_no_outliers = df[(z_scores >= -z_threshold) & (z_scores <= z_threshold)]
    return df_no_outliers


def time_series_plot(df, datetime_column, duration_column, member_column, member_value, casual_value, return_fig=False):
    """
    Create a time series plot for ride duration over time.

    Parameters:
    - df: DataFrame containing the data.
    - datetime_column: Name of the column with datetime values.
    - duration_column: Name of the column with ride duration values (in minutes as a float).
    - member_column: Name of the column indicating member or casual status.
    - member_value: Value indicating a member in the 'member_column'.
    - casual_value: Value indicating a casual user in the 'member_column'.
    """
    # Create separate DataFrames for member and casual users
    member_df = df[df[member_column] == member_value]
    casual_df = df[df[member_column] == casual_value]

    # Group data by date and calculate the mean duration for each date
    df = df.groupby(df[datetime_column].dt.date)[duration_column].mean().reset_index()
    member_df = member_df.groupby(member_df[datetime_column].dt.date)[duration_column].mean().reset_index()
    casual_df = casual_df.groupby(casual_df[datetime_column].dt.date)[duration_column].mean().reset_index()

    # Create an interactive time series plot using Plotly
    fig = px.line(df, x=datetime_column, y=duration_column, labels={'x': 'Date', 'y': 'Average Duration (minutes)'},
                  title='Ride Duration (Aggregated by Date) by Rider Type in 2023')

    # Add traces for member and casual data
    fig.add_scatter(x=member_df[datetime_column], y=member_df[duration_column], mode='lines+markers',
                    name='Members')
    fig.add_scatter(x=casual_df[datetime_column], y=casual_df[duration_column], mode='lines+markers',
                    name='Casual Users')
    fig.add_scatter(x=df[datetime_column], y=df[duration_column], mode='lines+markers',
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
    df.drop(['rideable_type', 'ride_id', 'start_station_id', 'end_station_id'], axis=1, inplace=True)
    df = df.dropna()

    df['distance'] = df.apply(lambda row: haversine_distance(row['start_lat'], row['start_lng'],
                                                             row['end_lat'], row['end_lng']), axis=1)
    # Check for time!!
    df = df[df['distance'] != 0]

    # Convert to datetime format to find the time elapsed during rides
    df = ride_duration(df, 'started_at', 'ended_at')

    # Plot overlapping Plotly KDE plots for distance travelled for members vs casual users
    # create_dist_kde(df, 'member_casual', 'distance')

    # create_bubble_chart(df, 'distance', 'member_casual')

    # Generate the time series plot
    # time_series_plot(df, 'started_at', 'ride_duration_minutes', 'member_casual', 'member', 'casual')

    # Save the DataFrame to a CSV file
    df.to_csv('bluebike_updated.csv', index=False)

main()
