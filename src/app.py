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

# Load CSV data
df = pd.read_csv('https://raw.githubusercontent.com/thealphacubicle/'
                 'BlueBike-Dashboard/main/src/bluebike_trunc.csv')

# Create a Dash app instance with bootstrap styles
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the app layout
app.layout = dbc.Container([

    # Add a Navigation Bar as the title for the dashboard
    dbc.NavbarSimple(brand="Blue Bike Ridership Visualization",
                     color="lightblue", dark=False, id="nav-bar",
                     brand_style={"font-color": "black", 'text-align': 'center'}),

    # Add about section to project
    html.Div([
        html.H2("About the Project", style={'text-align': 'center', 'padding-top': '20px'}),

        # TODO: Edit description once everything else is done
        html.P("TO BE CHANGED.", style={'text-align': 'center', 'padding-top': '15px'})
    ]),

    dbc.Row([
        html.H2("Explore the Data", style={'text-align': 'center', 'padding-top': '20px'}),
        dbc.Col(
            dash_table.DataTable(
                df.head(100).to_dict('records'),
                [{"name": i, "id": i} for i in df.columns],
                style_table={'height': '300px', 'overflowY': 'auto'},
                fixed_rows={'headers': True},
                page_size=10
            )
        )
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='ride-type-bar-chart'), width=6),
        dbc.Col(dcc.Graph(id='rides-map'), width=6)
    ])
], fluid=True)


# Call back functions for the plots in dashboard
@app.callback(
    Output('ride-type-bar-chart', 'figure'),
    [Input('ride-type-bar-chart', 'id')]
)
def update_ride_type_bar_chart(_):
    fig = px.bar(df, x=df['rideable_type'].value_counts().index, y=df['rideable_type'].value_counts().values,
                 title="Ride Types")
    return fig


@app.callback(
    Output('rides-map', 'figure'),
    [Input('rides-map', 'id')]
)
def update_rides_map(_):
    fig = px.scatter_mapbox(df, lat="start_lat", lon="start_lng", color="rideable_type",
                            title="Start and End Points of Rides", mapbox_style="open-street-map")
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
