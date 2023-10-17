"""
Runs the Dash dashboard interface
DS3500 HW2
Authors: Srihari Raman & Reema Sharma
"""
from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import sankey as sk
import numpy as np
import math
import analysis


# Load CSV data
df = pd.read_csv('https://raw.githubusercontent.com/thealphacubicle/BlueBike-Dashboard/main/src/bluebike_updated.csv')


# Create a Dash app with bootstrap styles
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the app layout
app.layout = dbc.Container([

    html.H1('Blue Bike Ridership Visualization', style={'textAlign': 'center', 'color': 'black',
                                                        'backgroundColor': 'lightblue', 'padding': '10px'}),

    # First row
    dbc.Row([
        html.H2("Explore the Data:", style={'text-align': 'center', 'padding-top': '20px'}),

        # Select columns to explore dataset
        dbc.Col(children=[
            dbc.Label('Pick a column to explore: ', style={'padding-bottom': '10px'}),
            dcc.Dropdown(id='columns-eda-dropdown',
                         options=[{'label': col, 'value': col} for col in ['start_station_name', 'end_station_name',
                                                                           'member_casual', 'distance',
                                                                           'ride_duration_minutes']]
                         , value='member_casual', multi=False),

        ]),

        # Replace this with some other useful graph about chosen column
        html.H2("Column Visualization: ",
                style={'padding-top': '20px', 'font-weight': 'bold', 'text-align': 'center'}),
        dcc.Graph(id="column_statistics"),

    ]),

    # Displaying statistics of selected column
    html.H2("Key Metrics: ", style={'padding-top': '20px', 'font-weight': 'bold', 'text-align': 'center'}),
    html.Div(
        [
            html.H4("Choose A Ride Group:"),
            dbc.RadioItems(
                options=[
                    {"label": "Member", "value": 'member'},
                    {"label": "Casual", "value": 'casual'},
                ],
                value='member',
                id="radioitems-input",
            ),
        ]),

    # Add dynamic indicators for metrics
    dbc.Row([
        dbc.Col(dcc.Graph(id='mean_indicator'), width=4),
        dbc.Col(dcc.Graph(id='ride_duration_indicator'), width=4),
        dbc.Col(dcc.Graph(id='speed_avg_indicator'), width=4)
    ]),

    html.Hr()

], style={'backgroundColor': 'white', 'padding': '20px'}, fluid=True)


@app.callback(Output("column_statistics", "figure"), Input('columns-eda-dropdown', 'value'))
def viz_statistics_of_column(column):
    """
    Callback function that displays a relevant chart as to the data in the column using type inference.
    By default, columns ID columns and latitude/longitude data will not be shown

    :param column: Column to display information for
    :returns fig: Plotly figure with relevant data
    """
    # Compute the value counts
    value_counts = df[column].value_counts()
    places = ['start_station_name', 'end_station_name']

    if column is None:
        column = "member_casual"
    # Displaying sankey diagram for columns that are departure/arrival stations
    elif column in places:
        counts_df = sk.create_value_column(df, ['member_casual', column], 'count')

        counts_df = counts_df[counts_df['count'] >= 850]

        fig = sk.make_sankey(counts_df, 'member_casual', column,
                             vals=None, return_fig=True, title_text=f"Member Type to {column}")

    # Graph distance
    elif column == 'distance':
        fig = analysis.create_dist_kde(df, 'member_casual', column, return_fig=True)
        fig.update_xaxes(range=[0, math.ceil(np.quantile(df[column], 0.75) * 2.25)])

    elif column == 'ride_duration_minutes':
        fig = analysis.create_violin_plot(df, 'ride_duration_minutes', 'member_casual', return_fig=True)

    elif column == 'member_casual':
        fig = px.scatter_mapbox(df, lat="start_lat", lon="start_lng", opacity=0.9, zoom=10,
                                color='member_casual',
                                title="Selection Points of All Rides", mapbox_style="open-street-map")

    # All other columns, just show value_counts by default
    else:
        fig = px.bar(
            data_frame=value_counts.reset_index(),
            x=column,
            y='count',
            labels={'index': 'Category', 'column_name': 'Count'}
        )

    return fig


@app.callback(Output('mean_indicator', 'figure'), Input("radioitems-input", "value"))
def mean_column_indicator(column):
    filtered_df = df[df['member_casual'] == column]

    figure = go.Figure(go.Indicator(
        mode='number',
        number={"prefix": "", "suffix": " miles"},
        value=filtered_df['distance'].mean(),
        title={'text': "Average Distance of Rides "}))

    return figure


@app.callback(Output('ride_duration_indicator', 'figure'), Input("radioitems-input", "value"))
def ride_duration_indicator(column):
    filtered_df = df[df['member_casual'] == column]

    figure = go.Figure(go.Indicator(
        mode='number',
        number={"prefix": "", "suffix": " minutes"},
        value=filtered_df['ride_duration_minutes'].mean(),
        title={'text': "Average Ride Duration "}))

    return figure


@app.callback(Output('speed_avg_indicator', 'figure'), Input("radioitems-input", "value"))
def speed_indicator(column):
    filtered_df = df[df['member_casual'] == column]
    figure = go.Figure(go.Indicator(
        mode='number',
        value=np.mean(list(filtered_df['distance'] / filtered_df['ride_duration_minutes'])),
        number={"prefix": "", "suffix": " mph"},
        title={'text': "Average Speed of All Riders"}))

    return figure


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
