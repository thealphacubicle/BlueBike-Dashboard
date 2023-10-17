"""
Runs the Dash dashboard interface
DS3500 HW2
Authors: Srihari Raman & Reema Sharma
"""
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import sankey as sk
import numpy as np
import math
import analysis

# https://raw.githubusercontent.com/thealphacubicle/BlueBike-Dashboard/main/src/bluebike_updated.csv

# Load CSV data
df = pd.read_csv('/Users/srihariraman/PycharmProjects/BlueBike-Dashboard/src/bluebike_updated.csv')

# Create a Dash app with bootstrap styles
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the app layout
app.layout = dbc.Container([

    html.H1('Blue Bike Ridership Visualization', style={'textAlign': 'center', 'color': 'black',
                                                        'backgroundColor': 'lightblue', 'padding': '10px'}),

    # TODO: Add about section to project
    html.Div([
        html.H2("About the Project:", style={'text-align': 'center', 'padding-top': '20px'}),

        # TODO: Edit description once everything else is done
        html.P("TO BE CHANGED.", style={'text-align': 'center', 'padding-top': '15px'}),
        html.Hr()
    ]),

    # First row
    dbc.Row([
        html.H2("Explore the Data:", style={'text-align': 'center', 'padding-top': '20px'}),

        # Select columns to explore dataset
        dbc.Col(children=[
            dbc.Label('Pick a column to explore: ', style={'padding-bottom': '10px'}),
            dcc.Dropdown(id='columns-eda-dropdown',
                         options=[{'label': col, 'value': col} for col in df.columns
                                  if col in ['start_station_name', 'end_station_name', 'member_casual', 'distance',
                                             'ride_duration_minutes']]
                         ,
                         value=df.columns[-3], multi=False),

            # Describing the selected column
            dbc.Label("Description: ", style={'padding-top': '35px', 'font-weight': 'bold'}),
            html.P(children="CREATE CALLBACK FUNCTION TO INSERT METADATA DESCRIPTION HERE!!!",
                   style={'padding-top': '10px', 'padding-bottom': '15px'}, id="column_description_text"),

            # Replace this with some other useful graph about chosen column
            html.H2("Column Visualization: ",
                    style={'padding-top': '20px', 'font-weight': 'bold', 'text-align': 'center'}),
            dcc.Graph(id="column_statistics"),

        ]),

        # Displaying statistics of selected column with indicators
        html.H2("Key Metrics: ", style={'padding-top': '20px', 'font-weight': 'bold', 'text-align': 'center'}),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=go.Figure(go.Indicator(
                mode='number',
                value=np.mean(list(df['distance'])),
                number={"prefix": "", "suffix": " miles"},
                title={'text': "Average Distance of Rides "})),
            ), width=4),
            dbc.Col(dcc.Graph(figure=go.Figure(go.Indicator(
                mode='number',
                value=np.mean(list(df['ride_duration_minutes'])),
                number={"prefix": "", "suffix": " min"},
                title={'text': "Average Ride Duration"})),
            ), width=4),
            dbc.Col(dcc.Graph(figure=go.Figure(go.Indicator(
                mode='number',
                value=np.mean(list(df['distance'] / df['ride_duration_minutes'])),
                number={"prefix": "", "suffix": " mph"},
                title={'text': "Average Speed of All Riders"})),
            ), width=4)
        ]),

        html.Hr()
    ]),

    # TODO: Format the radio items nicely
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(
                id='radio-ride-type',
                options=[
                    {'label': 'All', 'value': 'rideable_type'},
                    {'label': 'Member', 'value': 'member'},
                    {'label': 'Casual', 'value': 'casual'},  # Replace accordingly
                ],
                labelStyle={'display': 'block'}
        )),
        dbc.Col(dcc.Graph(id='rides-map'), width=6)
    ])
], style={'backgroundColor': 'white', 'padding': '20px'}, fluid=True)


########################################################################################################################
# TODO: CREATE CALLBACK FUNCTIONS FOR ALL DYNAMIC ELEMENTS

# TODO: Create a metadata dictionary to map column to respective description
@app.callback(Output("column_description_text", "children"), Input('columns-eda-dropdown', 'value'))
def print_column_info(column):
    """
    Callback function to print the selected column's metadata
    :param column: Column selected from dropdown menu
    :return: Text about the column
    """
    return f"Replace with information about {column}!!!"


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

    # Displaying sankey diagram for columns that are departure/arrival stations
    if column in places:
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

    # All other columns, just show value_counts by default
    else:
        fig = px.bar(
            data_frame=value_counts.reset_index(),
            x=column,
            y='count',
            labels={'index': 'Category', 'column_name': 'Count'}
        )

    return fig


# TODO: Map update not working when "All" selected
@app.callback(Output('rides-map', 'figure'), Input('radio-ride-type', 'value'))
def update_rides_map(user_type):
    filtered_df = df[df['member_casual'] == user_type]

    fig = px.scatter_mapbox(filtered_df, lat="start_lat", lon="start_lng", color="rideable_type",
                            title="Selection Points of All Rides", mapbox_style="open-street-map")

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
