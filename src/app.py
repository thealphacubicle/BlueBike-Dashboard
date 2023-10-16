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

# Load CSV data
df = pd.read_csv('https://raw.githubusercontent.com/thealphacubicle/'
                 'BlueBike-Dashboard/main/src/bluebike_trunc.csv')

# Create a Dash app with bootstrap styles
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the app layout
app.layout = dbc.Container([

    # TODO: Change background color to white
    # Dashboard navbar
    dbc.NavbarSimple(
        brand="Blue Bike Ridership Visualization",
        color="blue",
        dark=True,
        id="nav-bar",
        style={'background': 'black', 'color': 'white', 'text-align': 'center'},
        brand_style={'fontSize': '40px'}),

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
                         options=[{'label': col, 'value': col} for col in df.columns if 'id' not in col and 'lat' not in
                                  col and 'lng' not in col]
                         ,
                         value=df.columns[-1], multi=False),

            # Describing the selected column
            dbc.Label("Description: ", style={'padding-top': '35px', 'font-weight': 'bold'}),
            html.P(children="CREATE CALLBACK FUNCTION TO INSERT METADATA DESCRIPTION HERE!!!",
                   style={'padding-top': '10px', 'padding-bottom': '15px'}, id="column_description_text"),


            # TODO: Displaying statistics of selected column with indicators
            html.H2("Statistics: ", style={'padding-top': '20px', 'font-weight': 'bold', 'text-align': 'center'}),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=go.Figure(go.Indicator(
                    mode='number',
                    value=000,
                    number={"prefix": "", "suffix": " miles"},
                    title={'text': "Average Distance of Rides "})),
                ), width=4),
                dbc.Col(dcc.Graph(figure=go.Figure(go.Indicator(
                    mode='number',
                    value=000,
                    number={"prefix": "", "suffix": " min"},
                    title={'text': "Average Ride Duration"})),
                ), width=4),
                dbc.Col(dcc.Graph(figure=go.Figure(go.Indicator(
                    mode='number',
                    value=000,
                    number={"prefix": "", "suffix": " mph"},
                    title={'text': "Average Speed of All Riders"})),
                ), width=4)
            ]),
        ]),

        # TODO: Replace this with some other useful graph about chosen column
        dcc.Graph(id="column_statistics"),

        html.Hr()
    ]),

    # Add two other useful graphs
    dbc.Row([
        # TODO: Edit this ride type graph -> it's redundant and useless
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
        fig = px.bar(
            data_frame=value_counts.reset_index(),
            x=column,
            y='count',
            labels={'index': 'Category', 'column_name': 'Count'},
            title=f'Visualizing Count:'
        )

    # Displaying sankey diagram for columns that are departure/arrival stations
    elif column in places:
        counts_df = sk.create_value_column(df, ['member_casual', column], 'count')

        counts_df = counts_df[counts_df['count'] >= 850]

        fig = sk.make_sankey(counts_df, 'member_casual', column,
                             vals=None, return_fig=True)

    # Figure out how to deal with started_at, ended_at columns
    else:
        fig = None

    return fig

# TODO: Replace this function with KDE plot for distances
@app.callback(Output('ride-type-bar-chart', 'figure'), [Input('ride-type-bar-chart', 'id')])
def update_ride_type_bar_chart(_):
    fig = px.bar(df, x=df['rideable_type'].value_counts().index, y=df['rideable_type'].value_counts().values,
                 title="Ride Types")
    return fig


@app.callback(Output('rides-map', 'figure'), [Input('rides-map', 'id')])
def update_rides_map(_):
    fig = px.scatter_mapbox(df, lat="start_lat", lon="start_lng", color="rideable_type",
                            title="Selection Points of All Rides", mapbox_style="open-street-map")

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
