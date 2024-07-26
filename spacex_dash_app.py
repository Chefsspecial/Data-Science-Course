# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': site, 'value': site} for site in launch_sites]
dropdown_options.insert(0, {'label': 'All Sites', 'value': 'ALL'})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),
                                html.Div(
                                    dcc.Dropdown(
                                        id='site-dropdown',                        
                                        options=dropdown_options,
                                        value='ALL',
                                        placeholder="Select a Launch Site here",
                                        searchable=True
                                    )
                                ),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.P("Payload range (Kg):"),
                                html.Div(dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    marks={0: '0', 10000: '10000'},
                                    value=[min_payload, max_payload]
                                )),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ]),

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # Filter the dataframe based on the selected site
    if entered_site == 'ALL':
        # Use the entire dataframe for 'ALL'
        df_to_plot = spacex_df
        title = 'All Launches'
    else:
        # Filter for the selected site
        df_to_plot = spacex_df[spacex_df['Launch Site'] == entered_site]
        title = f'Successful launches for {entered_site}'

    # Calculate success and failure counts
    success_count = df_to_plot[df_to_plot['class'] == 1].shape[0]
    failure_count = df_to_plot[df_to_plot['class'] == 0].shape[0]

    # Create the pie chart
    fig = px.pie(
        names=['Success', 'Failure'],
        values=[success_count, failure_count],
        title=title
    )
    return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Start with the entire DataFrame
    filtered_df = spacex_df.copy()

    # Debugging: Print initial data shape
    print(f"Initial data shape: {filtered_df.shape}")

    # Filter based on the selected site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Debugging: Print data shape after site filtering
    print(f"Data shape after site filtering: {filtered_df.shape}")

    # Further filter based on the payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    # Debugging: Print data shape after payload range filtering
    print(f"Data shape after payload range filtering: {filtered_df.shape}")

    # Check if there is data to plot
    if filtered_df.empty:
        print("No data to plot.")
        fig = px.scatter(
            x=[], y=[],
            title='No Data Available',
            labels={'x': 'Payload Mass (kg)', 'y': 'Launch Outcome'}
        )
    else:
        # Create the scatter plot
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload Mass vs. Launch Success by Booster Version',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )

    # Print figure data for debugging
    print(f"Figure data: {fig.to_dict()}")
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8090)