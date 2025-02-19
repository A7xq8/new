# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload values
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Sites
    # Dropdown for Launch Sites
dcc.Dropdown(
    id='site-dropdown',
    options=[
        {'label': 'All Sites', 'value': 'ALL'}
    ] + [
        {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
    ],
    value='ALL',
    placeholder="Select a Launch Site",
    searchable=True
),
    html.Br(),

    # Pie Chart for Success Count
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Payload Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload)+1, 2000)},
        value=[min_payload, max_payload]
    ),
    
    # Scatter Chart for Payload vs. Success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, names='Launch Site', values='class', 
                     title="Total Successful Launches for All Sites")
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(success_counts, names='class', values='count', 
                     title=f"Success vs. Failure for {selected_site}")
    return fig

# Callback for Scatter Chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title="Payload vs. Success",
                     labels={'class': 'Launch Outcome'},
                     hover_data=['Launch Site'])
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)