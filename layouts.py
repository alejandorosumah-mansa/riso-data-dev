# layouts.py
from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
#from application import application
#from data import load_data,load_categories,load_regions_geojson,load_district_geojson,get_district_id,departments_given_region

# layouts.py
from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
#from data import load_data
import pandas as pd
#from data import load_data
import plotly.graph_objects as go

from data import DataCollection

DataCollectionObject = DataCollection()

df,region_aggregated = DataCollectionObject.load_data()
list_of_categories = DataCollectionObject.load_categories()
# Enhanced Dropdown for Dynamic Filtering
country_options = [{'label': country, 'value': country} for country in df['REGION'].unique()]
product_options = [{'label': product, 'value': product} for product in df['Département'].unique()]

import plotly.graph_objects as go

graph_style = {
    'plot_bgcolor': '#343a40',  # Dark grey background
    'paper_bgcolor': '#343a40',
    'font': {
        'color': '#ffffff',  # White font color for better contrast
        'family': "Arial, Helvetica, sans-serif"  # Aesthetic font choice
    }
}

# Camel color palette for graphs
camel_palette = ['#f8f3ec', '#e4d1c0', '#c8a798', '#967860', '#5b4339', '#000000']



from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
#from data import load_data
import plotly.graph_objects as go

#df,region_aggregated = load_data()

# Global style for Plotly graphs
graph_style = {
    'plot_bgcolor': '#343a40',
    'paper_bgcolor': '#343a40',
    'font': {
        'color': '#ffffff',
        'family': "Arial, Helvetica, sans-serif"
    }
}

# Additional layouts (product and market analysis) would follow similar patterns, with more graphs and potentially dynamic content or advanced filters.





# In layouts.py, add this div in each page layout or in a common component used by all layouts
animation_div = html.Div(id='animation-overlay', children=[html.Div(className='dash-element')], style={'display': ''})

# Function updated to generate specific graphs based on the title
def generate_figure(dataframe,dataframe2, graph_type):
    if graph_type == 'Line Chart':
        # Example: Sales over time line chart
        fig = px.bar(dataframe, x='Date', y='Culture', color='REGION', title='Sales Over Time')
    elif graph_type == 'Map':
        senegal_regions_geojson,feature = DataCollectionObject.load_regions_geojson()
        fig = go.Figure(go.Choroplethmapbox(geojson=senegal_regions_geojson,
                                        locations=[feature['id'] for feature in senegal_regions_geojson['features']],
                                        z=list(range(len(senegal_regions_geojson['features']))),  # Assigning a unique value for color differentiation
                                        colorscale="Viridis",
                                        marker_opacity=0.5,
                                        marker_line_width=0))
                             
        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=5, mapbox_center={"lat": 14.4974, "lon": -14.4524})
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    elif graph_type =='Regional Map':
                # Create the choropleth map
        data,geojson_data = DataCollectionObject.load_district_geojson()
        Region  = "Tambacounda"
        specific_district_list_name = DataCollectionObject.regions_departments[Region]
        specific_district_list = []
        for i in specific_district_list_name:
            specific_district_list.append(DataCollectionObject.get_district_id(i))

        data['plot_color'] = 0  # Default for gray
        data.loc[data['District_ID'].isin(specific_district_list), 'plot_color'] = 1  # Change to 1 for Viridis-like color



        # Define the figure with Choroplethmapbox
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=data['District_ID'],
            featureidkey="properties.adm2cd",
            z=data['plot_color'],
            colorscale=[(0, 'gray'), (0.5, 'gray'), (0.5, '#440154'), (1, '#440154')],  # Ensures a sharp transition
            marker_opacity=0.5,
            hoverinfo='text',
            hovertext=data['District_Name'],
            marker_line_color='black',
            marker_line_width=1
        ))

        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=5, mapbox_center={"lat": 14.4974, "lon": -14.4524})
        fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
            #fig.show()

    elif graph_type == '3D Scatter':
        # Example: 3D Scatter plot
        fig = px.scatter(dataframe2, x='Production en tonne', y='Rendement kg/ha', color='REGION',hover_name="REGION",log_x=True, title='View of Production and Culture by Region',size="Superficie en ha")
    
    else:
        # Default to a simple bar chart if graph_type is not recognized
        fig = px.bar(dataframe, x='Département', y='Production', color='Département', title='Sales by Product')
    
    fig.update_layout(**graph_style)  # Apply the global graph style
    return fig

# Home Layout with diversified graphs
#home_layout = dbc.Container([
#    dbc.Row(html.H3('HOME', className='mb-16 text-light')),
#    dbc.Row([
#        dbc.Col(dcc.Graph(id='line-chart', figure=generate_figure(df, 'Line Chart')), width=6),
#        dbc.Col(dcc.Graph(id='map', figure=generate_figure(df, 'Map')), width=6),
#    ], className='mb-2'),
#    dbc.Row([
#        dbc.Col(dcc.Graph(id='3d-scatter', figure=generate_figure(df, '3D Scatter')), width=12),
#    ])
#], fluid=True)

# Advanced filters
advanced_filters_layout = html.Div([
    dbc.Row([
        dbc.Col(dcc.Input(id='text-search', type='text', placeholder='Search Products...', className='mb-2')),
        dbc.Col(dcc.Checklist(
            id='boolean-filter',
            options=[{'label': 'Available', 'value': 'AVL'}, {'label': 'On Sale', 'value': 'SAL'}],
            value=['AVL', 'SAL'],
            className='mb-2'
        )),
        dbc.Col(dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            className='mb-2'
        )),
    ])
])

# Incorporating advanced filters into the home layout
home_layout = dbc.Container([
    dcc.Interval(id='animation-timer', interval=10000, max_intervals=1) , # 2 seconds timer,
    animation_div,

    html.Br(),
    html.H1('DATA - SENEGAL', className='mb-4 text-light'),  # Adding a title for the home page

    html.Div([
        
        html.P('Welcome to DATA - SENEGAL, your gateway to agricultural insights in Senegal.'),
        html.P('Explore the data visualizations below to gain valuable insights into the agricultural landscape of Senegal.'),
        #html.Img(src='/assets/senegal_map.jpg', alt='Senegal Map', style={'width': '100%', 'height': 'auto', 'margin-top': '20px'})
    ], className='mb-4'),  # Adding a div for information and an image of Senegal

    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart', figure=generate_figure(df,region_aggregated, 'Line Chart')), width=6),
        dbc.Col(dcc.Graph(id='map', figure=generate_figure(df,region_aggregated, 'Map')), width=6),
        html.Div(id='region-click-info', children='Click on a region in the map'),
       
    ], className='mb-2'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='3d-scatter', figure=generate_figure(df,region_aggregated, '3D Scatter')), width=12),
    ]),
    #advanced_filters_layout,  # Including advanced filters at the top
    # The rest of the layout follows as previously defined...
], fluid=True)

# Incorporating advanced filters into the home layout
regional_layout = dbc.Container([
    html.Br(),
    html.H1('DATA - REGIONAL', className='mb-4 text-light', id="Header_text"),  # Adding a title for the home page

    html.Div([
        
        html.P('Welcome to DATA - REGIONAL, your gateway to agricultural insights in Senegal.', id="Subheader_text"),
        html.P('Explore the data visualizations below to gain valuable insights into the agricultural landscape of Senegal.'),
        #html.Img(src='/assets/senegal_map.jpg', alt='Senegal Map', style={'width': '100%', 'height': 'auto', 'margin-top': '20px'})
    ], className='mb-4'),  # Adding a div for information and an image of Senegal

    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart', figure=generate_figure(df,region_aggregated, 'Line Chart')), width=6),
        dbc.Col(dcc.Graph(id='map', figure=generate_figure(df,region_aggregated, 'Regional Map')), width=6),
        #html.Div(id='region-click-info', children='Click on a region in the map'),
    ], className='mb-2'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='3d-scatter', figure=generate_figure(df,region_aggregated, '3D Scatter')), width=12),
    ]),
    #advanced_filters_layout,  # Including advanced filters at the top
    # The rest of the layout follows as previously defined...
], fluid=True)

# Incorporating advanced filters into the home layout
district_layout = dbc.Container([
    html.Br(),
    html.H1('DATA - DISTRICT', className='mb-4 text-light'),  # Adding a title for the home page

    html.Div([
        
        html.P('Welcome to DATA - DISTRICT, your gateway to agricultural insights in Senegal.'),
        html.P('Explore the data visualizations below to gain valuable insights into the agricultural landscape of Senegal.'),
        #html.Img(src='/assets/senegal_map.jpg', alt='Senegal Map', style={'width': '100%', 'height': 'auto', 'margin-top': '20px'})
    ], className='mb-4'),  # Adding a div for information and an image of Senegal

    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart', figure=generate_figure(df,region_aggregated, 'Line Chart')), width=6),
        dbc.Col(dcc.Graph(id='map', figure=generate_figure(df,region_aggregated, 'Regional Map')), width=6),
        html.Div(id='region-click-info', children='Click on a region in the map'),
    ], className='mb-2'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='3d-scatter', figure=generate_figure(df,region_aggregated, '3D Scatter')), width=12),
    ]),
    #advanced_filters_layout,  # Including advanced filters at the top
    # The rest of the layout follows as previously defined...
], fluid=True)



# Update layouts for product and market analysis similarly...


# Product Analysis Page Layout
product_sales = df.groupby('Département').agg({'Culture': 'sum'}).reset_index()

product_layout = dbc.Container([
    dbc.Row(html.H3('Département', className='mb-16 text-light')),
    dbc.Row([
        dbc.Col(dcc.RangeSlider(id='product-sales-range-slider', min=0, max=500, step=50, value=[100, 400], marks={i: str(i) for i in range(0, 501, 50)}), width=12),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='product-sales-distribution'), width=12),
    ]),
], fluid=True)


# Market Analysis Page Layout
country_sales = df.groupby('REGION').agg({'Culture': 'sum'}).reset_index()

market_layout = dbc.Container([
    dbc.Row(html.H3('MARKET', className='mb-16 text-light')),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='market-country-dropdown', options=country_options, value='USA', multi=True), width=12),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dcc.Graph(id='market-sales-by-country'), width=12),
    ]),
], fluid=True)