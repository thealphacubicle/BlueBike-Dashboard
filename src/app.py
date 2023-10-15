"""
Runs the Dash dashboard interface
DS3500 HW2
Authors: Srihari Raman & Reema Sharma
"""

# Required imports
from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import sankey as sk

# Load CSV data
df = pd.read_csv('https://raw.githubusercontent.com/thealphacubicle/'
                 'BlueBike-Dashboard/main/src/bluebike_trunc.csv')

# Create a Dash app instance with bootstrap styles
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the app layout
app.layout = dbc.Container([

    # TODO: Change background color to white
    # Add a Navigation Bar as the title for the dashboard
    dbc.NavbarSimple(brand="Blue Bike Ridership Visualization",
                     color="blue", dark=False, id="nav-bar",
                     style={'background': 'black',
                            'font-color': "lightblue", 'text-align': 'center'},
                     brand_style={'fontSize': '40px'}),

    # Add about section to project
    html.Div([
        html.H2("About the Project", style={'text-align': 'center', 'padding-top': '20px'}),

        # TODO: Edit description once everything else is done
        html.P("TO BE CHANGED.", style={'text-align': 'center', 'padding-top': '15px'}),
        html.Hr()
    ]),

    # First row
    dbc.Row([
        html.H2("Explore the Data", style={'text-align': 'center', 'padding-top': '20px'}),

        # Form to select columns to explore dataset
        dbc.Col(children=[
            dbc.Label('Pick a column to explore: ', style={'padding-bottom': '10px'}),
            dcc.Dropdown(id='columns-eda-dropdown',
                         options=[{'label': col, 'value': col} for col in df.columns if 'id' not in col and 'lat' not in
                                  col and 'lng' not in col]
                         ,
                         value=df.columns[-1], multi=False),

            dbc.Label("Description: ", style={'padding-top': '35px', 'font-weight': 'bold'}),
            html.P(children="CREATE CALLBACK FUNCTION TO INSERT METADATA DESCRIPTION HERE!!!",
                   style={'padding-top': '10px', 'padding-bottom': '15px'}, id="column_description_text"),

            dbc.Label("Statistics: ", style={'padding-top': '20px', 'font-weight': 'bold'}),
            dcc.Graph(id="column_statistics")

        ]),

        dbc.Col([
            #dbc.Col(dcc.Graph(id="column_statistics_num"), width=15),
        ]),

        html.Hr()
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='ride-type-bar-chart'), width=6),
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


# TODO: UPDATE IF ELSE WITH TYPE CHECK AND ACCORDING GRAPH DISPLAY
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

    # Displaying bar chart for columns that are numbers
    if column not in ['started_at', 'ended_at', 'start_station_name', 'end_station_name']:
        # Plot the value counts
        fig = px.bar(
            data_frame=value_counts.reset_index(),
            x=column,
            y='count',
            labels={'index': 'Category', 'column_name': 'Count'},
            title=f'Visualizing Count:'
        )

    # Displaying sankey diagram for columns that are departure/arrival stations
    elif column in places:
        other_column = places[1 - places.index(column)]

        print(column, other_column)
        counts_df = sk.create_value_column(df, ['member_casual', column], 'count')

        counts_df = counts_df[counts_df['count'] >= 850]

        fig = sk.make_sankey(counts_df, 'member_casual', column,
                       vals=None, return_fig=True)

    return fig


# TODO: Write code for indicator (dependent on column dtype)
# @app.callback(Output("column_statistics_num", "figure"), Input('columns-eda-dropdown', 'value'))
# def num_statistics_of_column(column):
#     """
#     Callback function to display an indicator about the column (dependent on column value type)
#     :param column: Column to display information about
#     :return: Indicator GO figure
#     """
#     pass


# TODO: Replace this function with KDE plot for distances
@app.callback(Output('ride-type-bar-chart', 'figure'), [Input('ride-type-bar-chart', 'id')])
def update_ride_type_bar_chart(_):
    fig = px.bar(df, x=df['rideable_type'].value_counts().index, y=df['rideable_type'].value_counts().values,
                 title="Ride Types")
    return fig


# TODO: Use distance column in df to create bubble map of origin/destination info for bikes
@app.callback(Output('rides-map', 'figure'), [Input('rides-map', 'id')])
def update_rides_map(_):
    fig = px.scatter_mapbox(df, lat="start_lat", lon="start_lng", color="member_casual",
                            title="Start and End Points of Rides", mapbox_style="open-street-map")

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
