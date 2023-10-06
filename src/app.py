from dash import Dash, html, dcc, Input, Output

import plotly.express as px
import pandas as pd


data = pd.read_csv("/Users/srihariraman/PycharmProjects/DS3500/HW/HW2/data/mbta_cr_data.csv")

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1('Sample Dash Dashboard'),

    dcc.Graph(id='scatter-plot'),

    dcc.Slider(
        id='slider',
        min=data['x'].min(),
        max=data['x'].max(),
        step=1,
        value=data['x'].min(),
        marks={str(x): str(x) for x in data['x'].unique()}
    ),
])


# Define callback to update the scatter plot based on slider value
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('slider', 'value')]
)
def update_scatter_plot(selected_value):
    filtered_data = data[data['x'] == selected_value]
    fig = px.scatter(filtered_data, x='x', y='y', title=f'Scatter Plot for x={selected_value}')
    return fig


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)