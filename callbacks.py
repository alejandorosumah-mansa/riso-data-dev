from dash.dependencies import Input, Output, State
from dash import dcc, html
import layouts
import dash
import dash_bootstrap_components as dbc
from appflask import application
from data import load_data,region_conversion,load_district_geojson,get_district_id,departments_given_region,id_to_union
import plotly.express as px
from dash import html
import pandas as pd
import plotly.graph_objects as go
import json

import time
# Global style for Plotly graphs
graph_style = {
    'plot_bgcolor': '#343a40',  # Dark grey background
    'paper_bgcolor': '#343a40',
    'font': {
        'color': '#ffffff',  # White font color for better contrast
        'family': "Arial, Helvetica, sans-serif"  # Aesthetic font choice
    }
}
region_selection_global = ['DAKAR', 'DIOURBEL', 'FATICK', 'KAFFRINE', 'KAOLACK', 'KEDOUGOU', 'KOLDA', 'LOUGA', 'MATAM', 'SAINT-LOUIS', 'SEDHIOU', 'SENEGAL', 'TAMBACOUNDA', 'THIES', 'ZIGUINCHOR']
# Camel color palette for graphs
camel_palette = ['#f8f3ec', '#e4d1c0', '#c8a798', '#967860', '#5b4339', '#000000']

from dash.dependencies import Input, Output
from data import load_data,load_regions_geojson

def check_district(clickData, region_id):

    if clickData is not None:
        if any(i.isdigit() for i in region_id):
            return True
    return False
def generate_figure(dataframe,dataframe2, graph_type,y_value,title_graph,senegal_regions_geojson,feature,Region=None):
    if graph_type == 'Line Chart':
        
        # Example: Sales over time line chart
        
        if Region == None:
            fig = px.bar(dataframe, x='Date', y=y_value, color='REGION', title=title_graph)
        else:
            print("Will plot!")
            dataframe.to_csv("Test_csv.csv")
            fig = px.bar(dataframe, x='Date', y=y_value, color='Département', title=title_graph)
            #fig.write_image("images/fig1.png")
    elif graph_type == 'Map':
        # Example: Sales by country map visualization
        fig = go.Figure(go.Choroplethmapbox(geojson=senegal_regions_geojson,
                                        locations=[feature['id'] for feature in senegal_regions_geojson['features']],
                                        z=list(range(len(senegal_regions_geojson['features']))),  # Assigning a unique value for color differentiation
                                        colorscale="Viridis",
                                        marker_opacity=0.5,
                                      marker_line_width=0))
    elif graph_type == 'Regional Map':
        # Example: Sales by country map visualization
        data,geojson_data = load_district_geojson()
        
        specific_district_list_name = departments_given_region(Region)
        specific_district_list = []
        for i in specific_district_list_name:
            specific_district_list.append(get_district_id(i))

        data['plot_color'] = 0  # Default for gray
        data.loc[data['District_ID'].isin(specific_district_list), 'plot_color'] = 1  # Change to 1 for Viridis-like color


        # Define the figure with Choroplethmapbox
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=data['District_ID'],
            featureidkey="properties.adm2cd",
            z=data['plot_color'],
            colorscale=[(0, 'gray'), (0.5, 'gray'), (0.5, '#00bc8c'), (1, '#00bc8c')],  # Ensures a sharp transition
            marker_opacity=0.5,
            hoverinfo='text',
            hovertext=data['District_Name'],
            marker_line_color='black',
            marker_line_width=1
        ))

        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=5, mapbox_center={"lat": 14.4974, "lon": -14.4524})
        fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
            #fig.show()

        #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    elif graph_type == 'Producers Map':

        # Load the GeoJSON data
        

        geojson_data = senegal_regions_geojson
        token = open(".mapbox_token").read() # you will need your own token
        # Ensure that 'features' exists and is not empty
        if not geojson_data.get('features'):
            raise ValueError("No features in GeoJSON")

        # Since properties might be empty, we simulate some data values for all features
        # Creating a DataFrame to match the districts
        data = pd.DataFrame({
            'District_ID': [feature['id'] for feature in geojson_data['features']],
            'District_Name': [list(feature['properties'].keys())[0] for feature in geojson_data['features']],
            'plot_color': [1 if 'Ndelle' in list(feature['properties'].keys())[0] else -1 for feature in geojson_data['features']]
        })
        # Create the choropleth map
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=data['District_ID'],  # Use DataFrame index for locations
            z=data['District_ID'],  # Data values for coloring
            colorscale="Viridis",
            hovertext=data['District_Name'],
            marker_opacity=0.8,
            marker_line_width=0.8
        ))

        # We set the map center and zoom around the average coordinates of the first polygon
        # Handle different coordinate structures (multi-polygon vs. polygon)
        first_feature_geometry = geojson_data['features'][0]['geometry']

        # Assuming the geometry type is simple and extracting the first set of coordinates
        if first_feature_geometry['type'] == 'Polygon':
            first_polygon_coords = first_feature_geometry['coordinates'][0]
        elif first_feature_geometry['type'] == 'MultiPolygon':
            first_polygon_coords = first_feature_geometry['coordinates'][0][0]
        else:
            raise ValueError("Unsupported geometry type")

        # Calculate average latitude and longitude
        avg_lat = sum(coord[1] for coord in first_polygon_coords) / len(first_polygon_coords)
        avg_lon = sum(coord[0] for coord in first_polygon_coords) / len(first_polygon_coords)

        fig.update_layout(
            mapbox_zoom=8,  # Adjust zoom level if necessary
            mapbox_center={"lat": avg_lat, "lon": avg_lon},
            mapbox_style="dark",mapbox_accesstoken=token)

        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


    elif graph_type == '3D Scatter':
        # Example: 3D Scatter plot
        fig = px.scatter(dataframe2, x='Production en tonne', y='Rendement kg/ha', color='REGION',hover_name="REGION",log_x=True, title='View of Production and Culture by Region',size="Superficie en ha")
    else:
        # Default to a simple bar chart if graph_type is not recognized
        fig = px.bar(dataframe, x='Département', y='Production', color='Département', title='Sales by Product')
    
    fig.update_layout(**graph_style)  # Apply the global graph style
    return fig

@application.callback(
    Output('region-click-info', 'children'),
    [Input('crop-filter', 'value'),  # Text input for search
    Input('region-filter', 'value'),
    Input('indicator-filter', 'value'),  # Checklist for boolean conditions
    Input('date-slider', 'value'),
    Input('map', 'clickData')])
def display_region_click_info(crop_search, region_search,indicator_search, start_date, clickData):
    if clickData is not None:
            # Assuming 'id' or another identifiable attribute is in the clickData
        region_id = clickData['points'][0]['location']
        region_search = [region_id]
        
        region_selected = region_conversion(region_id, ActualNamesFirst=True)
        #update_graph(crop_search, region_search,indicator_search, start_date)
        return html.A("You clicked on the region: " + region_selected + ", do you want to navigate to the specific region? Click here to navigate.", href='/product-analysis'+"/region:" +region_selected, target='_blank')
@application.callback(
    [
        Output('line-chart', 'figure'),  # Assuming 'line-chart' is the ID of the graph you want to update
        Output('map', 'figure'),
        Output('region-filter', 'value')  # Update the dropdown value
    ],
    [Input('url', 'pathname'),Input('crop-filter', 'value'),  # Text input for search
     Input('region-filter', 'value'),
     Input('indicator-filter', 'value'),  # Checklist for boolean conditions
     Input('date-slider', 'value'),
     Input('map', 'clickData'),  # Start date from the date range picker # End date from the date range picker
     Input('last-clicked-region', 'children')],
    [State('region-filter', 'value')]
)
def update_graph_and_dropdown(url,crop_search, region_search, indicator_search, start_date, clickData, last_clicked_region, current_region_search):
    if 'region:' in url:
        region_name = url.split('region:')[1]
        Region  = region_name.title()
        specific_district_list_name = departments_given_region(Region)
        specific_district_list_name_upper = []
        for i in specific_district_list_name:
            specific_district_list_name_upper.append(i.upper())
        df, region_aggregated = load_data(groupby_selection="Département")
        if clickData == None:
            region_search = specific_district_list_name_upper
    else:
        df, region_aggregated = load_data()

    if clickData is not None:
        
        region_id = clickData['points'][0]['location']
        if any(i.isdigit() for i in region_id):
            
            region_selected = region_id
            print("ClickData: ", region_selected)
        else:
            region_selected = region_conversion(region_id, ActualNamesFirst=True)
        # Check if region_selected is already in region_search to avoid duplicates
        if region_selected not in current_region_search:
            if last_clicked_region and last_clicked_region not in current_region_search:
                region_search = [last_clicked_region]  # Exclusively select the clicked region
            else:
                region_search.append(region_selected)  # Append the selected region to the list
        elif region_selected in current_region_search:
            region_search.remove(region_selected)
    else:
        if 'region' in url:
            region_search = specific_district_list_name_upper
           
            
        else:
            region_selected = None
            region_search = current_region_search

    if region_search:
        # Best would be to append data to df and keep same structure
        # CHANGES TO MAKE:
            # 1. LOAD NEW DATA
            # 2. LOAD NEW MAP
            # 3. INSTEAD OF LINEMAP LINE, LOAD GRAPH
            # 4. BE ABLE TO COMPARE DIFFERENT GRAPHS, ONE VS OTHER
        if clickData is not None:
            if check_district(clickData,region_id):
                print("ClickData, REGION URL: ", region_selected)
                #load new dataset
                df = pd.read_csv("assets/district_data_complete.csv")
                list_unions = id_to_union(region_selected)
                print("List Unions: ", list_unions)
                region_search = list_unions
                df3 = df[df['Département'].isin(region_search)]
                #df[df["Department"].isin(list_unions)]

            # convertion between ID to unions
        print("Region Search: ", region_search)
        df = df[df['Département'].isin(region_search)]
        print("Shape DF: ", df.shape)

        #df.to_csv("testing/test.csv")
    if crop_search:
        #if clickData is not None:
        #    if check_district(clickData,region_id):
        #        df = pd.read_csv("assets/district_data_complete.csv")
        df = df[df['Culture'].isin(crop_search)]

    if indicator_search:
        if clickData is not None:
            if check_district(clickData,region_id):
                y_value = indicator_search
                print("Y VALUE: ", y_value)
                title_graph = indicator_search + " Per Production Area"
            else:
                y_value = indicator_search
                title_graph = indicator_search + " Per Region"
        else:
            y_value = indicator_search
            title_graph = indicator_search + " Per Region"


    if start_date[0] is None or start_date[1] is None:
        pass
    else:
        df = df[(df['Date'] >= start_date[0]) & (df['Date'] <= start_date[1])]
    if 'region:' in url:
        if clickData is not None:
            if check_district(clickData,region_id):
                # What will region_search be
                # Change all values
                # Title Graph -/, y_value -/, df-/, region_aggregated (won't be used),
                with open('map_production.geojson', 'r') as file:
                    senegal_regions_geojson = json.load(file)
                feature = None
                figure2 = generate_figure(df, region_aggregated, 'Producers Map', y_value, title_graph, senegal_regions_geojson, feature, Region)
                figure = generate_figure(df3, region_aggregated, 'Line Chart', y_value, title_graph, senegal_regions_geojson, feature,Region)
                
                return figure,figure2, region_search
            
        region_name = url.split('region:')[1]
        Region  = region_name.title()
        senegal_regions_geojson, feature = load_regions_geojson()
        figure = generate_figure(df, region_aggregated, 'Line Chart', y_value, title_graph, senegal_regions_geojson, feature,Region)
        figure2 = generate_figure(df, region_aggregated, 'Regional Map', y_value, title_graph, senegal_regions_geojson, feature, Region)
        return figure,figure2, region_search
    else:
        senegal_regions_geojson, feature = load_regions_geojson()
        figure = generate_figure(df, region_aggregated, 'Line Chart', y_value, title_graph, senegal_regions_geojson, feature)
        figure2 = None
        return figure,figure2, region_search

@application.callback(
    Output('product-sales-distribution', 'figure'),
    [Input('product-sales-range-slider', 'value'),
     Input('crop-filter', 'value'),  # Text input for search
     Input('region-filter', 'value'),
     Input('indicator-filter', 'value'),  # Checklist for boolean conditions
     Input('date-slider', 'value'),  # Start date from the date range picker # End date from the date range picker
     Input('last-clicked-region', 'children'),
     Input('map', 'clickData'), Input('url','pathname')]
)
def update_regional_analysis(sales_range,crop_search, region_search, indicator_search, start_date, last_clicked_region,clickData,url):
    if 'region:' in url:

        df, region_aggregated = load_data(groupby_selection="Département")
    else:
        df, region_aggregated = load_data()
    filtered_df = df[(df['Production'] >= sales_range[0]) & (df['Production'] <= sales_range[1])]
    fig = px.bar(filtered_df, x='Département', y='Production', color='Département', title='Product Sales Distribution within Selected Range')
    fig.update_layout(**graph_style)
    return fig

@application.callback(
    Output('market-sales-by-country', 'figure'),
    [Input('market-country-dropdown', 'value'),
     Input('crop-filter', 'value'),  # Text input for search
     Input('region-filter', 'value'),
     Input('indicator-filter', 'value'),  # Checklist for boolean conditions
     Input('date-slider', 'value'),  # Start date from the date range picker # End date from the date range picker
     Input('last-clicked-region', 'children'),
     Input('map', 'clickData')]
)
def update_district_analysis(selected_countries,crop_search, region_search, indicator_search, start_date, last_clicked_region,clickData):
    df, region_aggregated = load_data()
    if not isinstance(selected_countries, list):
        selected_countries = [selected_countries]
    
    filtered_df = df[df['REGION'].isin(selected_countries)]
    fig = px.pie(filtered_df, names='REGION', values='Production', title='Market Sales by REGION')
    fig.update_layout(**graph_style)
    return fig

@application.callback(
    [
        Output('Header_text', 'children'),
        Output('Subheader_text', 'children'),
    ],
    [Input('url', 'pathname')]
)
def update_text(url):
    if 'region:' in url:
        region_name = url.split('region:')[1]
        Region  = region_name.title()
        
    header_text = f"Welcome to {Region}, see below your agricultural insights of {Region}."
    subheader_text = f"View the production and culture of {Region}"
    return header_text,subheader_text
# @application.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def render_regional_selection(pathname):



@application.callback(
    Output('animation-overlay', 'style'),
    [Input('url', 'pathname'), Input('animation-timer', 'n_intervals')]
)
def update_animation_style(pathname, n_intervals):
    ctx = dash.callback_context

    if not ctx.triggered:
        # Default to not displaying the animation
        return {'display': 'none'}

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'url':
        # When URL changes, show the animation
        return {'display': 'block', 'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%', 'background': 'rgba(255, 255, 255, 0.8)', 'z-index': '9999'}
    elif trigger_id == 'animation-timer':
        # After a set time, hide the animation
        return {'display': 'none'}

    # Default case to hide the animation
    return {'display': 'none'}


@application.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname == '/':
        return layouts.home_layout
    elif '/product-analysis' in pathname:
        if 'region:' in pathname:
            region_name = pathname.split('region:')[1]
            Region  = region_name
        return layouts.regional_layout
    elif '/market-analysis' in pathname:
        return layouts.district_layout
    # If the user tries to reach a different page, return a 404 message
    return html.Div([
        html.H1('404: Not found', className='text-danger'),
        html.Hr(),
        html.P(f"The pathname {pathname} was not recognised...")
    ])