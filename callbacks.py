import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from appflask import application
from data import DataCollection
import layouts

class GraphGenerator:

    def __init__(self, data_collection):
        self.data_collection = data_collection
        self.graph_style = {}
        self.title_graph = "Default Title"
        self.region = None
        self.feature = None

    def generate_figure(self, dataframe, dataframe2, graph_type, y_value, geojson_data):
        if graph_type == 'Line Chart':
            return self._generate_line_chart(dataframe, y_value)
        elif graph_type == 'Map':
            return self._generate_map(geojson_data)
        elif graph_type == 'Regional Map':
            return self._generate_regional_map()
        elif graph_type == 'Producers Map':
            return self._generate_producers_map(geojson_data)
        elif graph_type == "Knowledge Graph":
            return self._generate_knowledge_graph()
        elif graph_type == '3D Scatter':
            return self._generate_3d_scatter(dataframe2)
        else:
            return self._generate_default_bar_chart(dataframe)

    def _generate_line_chart(self, dataframe, y_value):
        fig = px.bar(dataframe, x='Date', y=y_value, color='Département' if self.region else 'REGION', title=self.title_graph)
        fig.update_layout(**self.graph_style)
        return fig

    def _generate_map(self, geojson_data):
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=[feature['id'] for feature in geojson_data['features']],
            z=list(range(len(geojson_data['features']))),
            colorscale="Viridis",
            marker_opacity=0.5,
            marker_line_width=0
        ))
        fig.update_layout(**self.graph_style)
        return fig

    def _generate_regional_map(self):
        data, geojson = self.data_collection.load_district_geojson()
        specific_district_list = [self.data_collection.get_district_id(i) for i in self.data_collection.regions_departments[self.region]]
        data['plot_color'] = data['District_ID'].isin(specific_district_list).astype(int)
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson,
            locations=data['District_ID'],
            featureidkey="properties.adm2cd",
            z=data['plot_color'],
            colorscale=[(0, 'gray'), (0.5, 'gray'), (0.5, '#00bc8c'), (1, '#00bc8c')],
            marker_opacity=0.5,
            hoverinfo='text',
            hovertext=data['District_Name'],
            marker_line_color='black',
            marker_line_width=1
        ))
        fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=5, mapbox_center={"lat": 14.4974, "lon": -14.4524})
        fig.update_layout(**self.graph_style)
        return fig

    def _generate_producers_map(self, geojson_data):
        token = self.data_collection.mapbox_token
        if not geojson_data.get('features'):
            raise ValueError("No features in GeoJSON")
        data = pd.DataFrame({
            'District_ID': [feature['id'] for feature in geojson_data['features']],
            'District_Name': [list(feature['properties'].keys())[0] for feature in geojson_data['features']],
            'plot_color': [1 if 'Ndelle' in list(feature['properties'].keys())[0] else -1 for feature in geojson_data['features']]
        })
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=data['District_ID'],
            z=data['plot_color'],
            colorscale="Viridis",
            hovertext=data['District_Name'],
            marker_opacity=0.8,
            marker_line_width=0.8
        ))
        first_feature_geometry = geojson_data['features'][0]['geometry']
        first_polygon_coords = first_feature_geometry['coordinates'][0][0] if first_feature_geometry['type'] == 'MultiPolygon' else first_feature_geometry['coordinates'][0]
        avg_lat = sum(coord[1] for coord in first_polygon_coords) / len(first_polygon_coords)
        avg_lon = sum(coord[0] for coord in first_polygon_coords) / len(first_polygon_coords)
        fig.update_layout(mapbox_zoom=8, mapbox_center={"lat": avg_lat, "lon": avg_lon}, mapbox_style="dark", mapbox_accesstoken=token)
        fig.update_layout(**self.graph_style)
        return fig

    def _generate_knowledge_graph(self):
        node_tonnage = self.node_calc()
        nodes = [{'data': {'id': name, 'label': f'{name} ({tonnage} tonnes)', 'weight': self.calculate_node_size(tonnage)}, 'classes': 'top-center'} for name, tonnage in node_tonnage.items()]
        edges = [{'data': {'source': u, 'target': v, 'width': self.calculate_edge_width(node_tonnage[u], node_tonnage[v])}} for u, v in [("Union de Ndelle", "Miller de Union de Ndiaye 8")]]
        elements = nodes + edges
        return cyto.Cytoscape(id='cytoscape', elements=elements, layout={'name': 'breadthfirst'}, style={'width': '100%', 'height': '500px'}, stylesheet=[
            {'selector': 'node', 'style': {'content': 'data(label)', 'width': 'data(weight)', 'height': 'data(weight)', 'text-valign': 'center', 'text-halign': 'center', 'background-color': '#6495ED'}},
            {'selector': 'edge', 'style': {'width': 'data(width)', 'line-color': '#FFD700', 'target-arrow-color': '#FFD700', 'target-arrow-shape': 'triangle'}}
        ])

    def _generate_3d_scatter(self, dataframe2):
        fig = px.scatter(dataframe2, x='Production en tonne', y='Rendement kg/ha', color='REGION', hover_name="REGION", log_x=True, title='View of Production and Culture by Region', size="Superficie en ha")
        fig.update_layout(**self.graph_style)
        return fig

    def _generate_default_bar_chart(self, dataframe):
        fig = px.bar(dataframe, x='Département', y='Production', color='Département', title='Sales by Product')
        fig.update_layout(**self.graph_style)
        return fig

class VisualizationApp:
    def __init__(self):
        """
        Initialize the VisualizationApp with necessary configurations.
        """
        self.data_collection = DataCollection()
        self.graph_generator = GraphGenerator(self.data_collection)
        self.graph_style = {
            'plot_bgcolor': '#343a40',
            'paper_bgcolor': '#343a40',
            'font': {
                'color': '#ffffff',
                'family': "Arial, Helvetica, sans-serif"
            }
        }
        self.region_selection_global = [x.upper() for x in self.data_collection.regions_departments]
        self.camel_palette = ['#f8f3ec', '#e4d1c0', '#c8a798', '#967860', '#5b4339', '#000000']

    def node_calc(self):
        """
        Calculate node tonnage for the knowledge graph.

        Returns:
            dict: A dictionary of nodes and their corresponding tonnage values.
        """
        return {
            "Union de Ndelle": 100, "Miller de Union de Ndelle 8": 150,
            "Union de Ndiaye": 180, "Miller de Union de Ndiaye 8": 160,
        }

    def calculate_node_size(self, tonnage):
        """
        Determine node size based on tonnage.

        Args:
            tonnage (int): The tonnage value.

        Returns:
            int: The calculated node size.
        """
        return 15 + tonnage / 10

    def calculate_edge_width(self, u_tonnage, v_tonnage):
        """
        Determine edge width based on tonnage.

        Args:
            u_tonnage (int): The tonnage value for node u.
            v_tonnage (int): The tonnage value for node v.

        Returns:
            float: The calculated edge width.
        """
        return 1 + (u_tonnage + v_tonnage) / 200

    def check_district(self, clickData, region_id):
        """
        Check if a region ID corresponds to a district.

        Args:
            clickData (dict): Data from a click event.
            region_id (str or int): The region ID to check.

        Returns:
            bool: True if the region ID corresponds to a district, False otherwise.
        """
        return isinstance(region_id, str) and clickData and any(i.isdigit() for i in region_id)

    def toggle_modal(self, n1, n2, is_open):
        """
        Toggle the modal dialog.

        Args:
            n1 (int): Number of clicks to open the modal.
            n2 (int): Number of clicks to close the modal.
            is_open (bool): Current state of the modal.

        Returns:
            bool: The new state of the modal.
        """
        return not is_open if n1 or n2 else is_open

    def update_elements(self, n_clicks):
        """
        Update the elements of the cytoscape graph.

        Args:
            n_clicks (int): Number of clicks to open the modal.

        Returns:
            list: The updated elements for the cytoscape graph.
        """
        if n_clicks > 0:
            node_tonnage = self.node_calc()
            nodes = [{'data': {'id': name, 'label': f'{name} ({tonnage} tonnes)', 'weight': self.calculate_node_size(tonnage)}, 'classes': 'top-center'} for name, tonnage in node_tonnage.items()]
            edges = [{'data': {'source': u, 'target': v, 'width': self.calculate_edge_width(node_tonnage[u], node_tonnage[v])}} for u, v in [("Union de Ndelle", "Miller de Union de Ndiaye 8")]]
            return nodes + edges
        return []

    def display_region_click_info(self, crop_search, region_search, indicator_search, start_date, clickData):
        """
        Display information about the clicked region.

        Args:
            crop_search (str): The selected crop.
            region_search (str): The selected region.
            indicator_search (str): The selected indicator.
            start_date (list): The selected date range.
            clickData (dict): Data from a click event on the map.

        Returns:
            A: A link to navigate to the specific region.
        """
        if clickData:
            region_id = clickData['points'][0]['location']
            region_selected = self.data_collection.region_conversion(region_id, ActualNamesFirst=True)
            return html.A(f"You clicked on the region: {region_selected}, do you want to navigate to the specific region? Click here to navigate.",
                          href=f'/product-analysis/region:{region_selected}', target='_blank')
        return None

    def update_graph_and_dropdown(self, url, crop_search, region_search, indicator_search, start_date, clickData, last_clicked_region, current_region_search):
        """
        Update the graph and dropdown based on user input.

        Args:
            url (str): The current URL.
            crop_search (str): The selected crop.
            region_search (list): The selected regions.
            indicator_search (str): The selected indicator.
            start_date (list): The selected date range.
            clickData (dict): Data from a click event on the map.
            last_clicked_region (str): The last clicked region.
            current_region_search (list): The current selected regions in the dropdown.

        Returns:
            tuple: The updated line chart figure, map figure, and region filter value.
        """
        region_selected = None
        if 'region:' in url:
            region_name = url.split('region:')[1]
            self.graph_generator.Region = region_name.title()
            specific_district_list_name = self.data_collection.regions_departments[self.graph_generator.Region]
            specific_district_list_name_upper = [i.upper() for i in specific_district_list_name]
            df, region_aggregated = self.data_collection.load_data(groupby_selection="Département")
            region_search = specific_district_list_name_upper if clickData is None else region_search
        else:
            df, region_aggregated = self.data_collection.load_data()

        if clickData:
            region_id = clickData['points'][0]['location']
            if isinstance(region_id, int):
                region_selected = "KNOWLEDGEGRAPH"
            elif any(i.isdigit() for i in region_id):
                region_selected = region_id
            else:
                region_selected = self.data_collection.region_conversion(region_id, ActualNamesFirst=True)
            if region_selected not in current_region_search:
                region_search = [last_clicked_region] if last_clicked_region and last_clicked_region not in current_region_search else region_search + [region_selected]
            else:
                region_search.remove(region_selected)
        else:
            region_search = specific_district_list_name_upper if 'region' in url else current_region_search

        if region_search:
            if clickData and self.check_district(clickData, region_id):
                df = self.data_collection.complete_district_data
                list_unions = self.data_collection.id_union_dict[region_selected]
                region_search = list_unions
                df3 = df[df['Département'].isin(region_search)]
            df = df[df['Département'].isin(region_search)]

        if crop_search:
            df = df[df['Culture'].isin(crop_search)]

        if indicator_search:
            y_value = indicator_search
            self.graph_generator.title_graph = f"{indicator_search} Per Region" if clickData is None or not self.check_district(clickData, region_id) else f"{indicator_search} Per Production Area"

        if start_date[0] is not None and start_date[1] is not None:
            df = df[(df['Date'] >= start_date[0]) & (df['Date'] <= start_date[1])]
        
        if 'region:' in url:
            self.graph_generator.region = region_name.title()
            if clickData and self.check_district(clickData, region_id):
                geojson_data = self.data_collection.union_geojson_data
                figure2 = self.graph_generator.generate_figure(df, region_aggregated,"Producers Map" ,y_value, geojson_data)
                figure = self.graph_generator.generate_figure(df3, region_aggregated,"Line Chart" , y_value, geojson_data)
                return figure, figure2, region_search
            elif region_selected == "KNOWLEDGEGRAPH":
                geojson_data = None
                df3 = df[df['Département'].isin(region_search)]
                figure2 = self.graph_generator.generate_figure(df, region_aggregated,"Knowledge Graph" , y_value, geojson_data)
                figure = self.graph_generator.generate_figure(df3, region_aggregated,'Line Chart',  y_value, geojson_data)
                return figure, figure2, region_search
            geojson_data, feature = self.data_collection.load_regions_geojson()
            self.graph_generator.title_graph = 'Line Chart'
            self.feature = feature
            figure = self.graph_generator.generate_figure(df, region_aggregated,'Line Chart', y_value, geojson_data)
            figure2 = self.graph_generator.generate_figure(df, region_aggregated,'Regional Map', y_value, geojson_data)
            return figure, figure2, region_search
        geojson_data, feature = self.data_collection.load_regions_geojson()
        self.feature = feature
        figure = self.graph_generator.generate_figure(df, region_aggregated,'Line Chart', y_value, geojson_data)
        figure2 = None
        return figure, figure2, region_search

    def update_regional_analysis(self, sales_range, crop_search, region_search, indicator_search, start_date, last_clicked_region, clickData, url):
        """
        Update the product sales distribution based on user input.

        Args:
            sales_range (list): The selected sales range.
            crop_search (str): The selected crop.
            region_search (list): The selected regions.
            indicator_search (str): The selected indicator.
            start_date (list): The selected date range.
            last_clicked_region (str): The last clicked region.
            clickData (dict): Data from a click event on the map.
            url (str): The current URL.

        Returns:
            Figure: The updated product sales distribution figure.
        """
        df, region_aggregated = self.data_collection.load_data(groupby_selection="Département") if 'region:' in url else self.data_collection.load_data()
        filtered_df = df[(df['Production'] >= sales_range[0]) & (df['Production'] <= sales_range[1])]
        fig = px.bar(filtered_df, x='Département', y='Production', color='Département', title='Product Sales Distribution within Selected Range')
        fig.update_layout(**self.graph_style)
        return fig

    def update_district_analysis(self, selected_countries, crop_search, region_search, indicator_search, start_date, last_clicked_region, clickData):
        """
        Update the market sales by country based on user input.

        Args:
            selected_countries (list): The selected countries.
            crop_search (str): The selected crop.
            region_search (list): The selected regions.
            indicator_search (str): The selected indicator.
            start_date (list): The selected date range.
            last_clicked_region (str): The last clicked region.
            clickData (dict): Data from a click event on the map.

        Returns:
            Figure: The updated market sales by country figure.
        """
        df, region_aggregated = self.data_collection.load_data()
        if not isinstance(selected_countries, list):
            selected_countries = [selected_countries]
        filtered_df = df[df['REGION'].isin(selected_countries)]
        fig = px.pie(filtered_df, names='REGION', values='Production', title='Market Sales by REGION')
        fig.update_layout(**self.graph_style)
        return fig

    def update_text(self, url):
        """
        Update the header and subheader text based on the current URL.

        Args:
            url (str): The current URL.

        Returns:
            tuple: The updated header and subheader text.
        """
        if 'region:' in url:
            region_name = url.split('region:')[1]
            Region = region_name.title()
            header_text = f"Welcome to {Region}, see below your agricultural insights of {Region}."
            subheader_text = f"View the production and culture of {Region}"
            return header_text, subheader_text
        return "Welcome to the Dashboard", "View the production and culture data"

    def update_animation_style(self, pathname, n_intervals):
        """
        Update the style of the animation overlay based on the URL and timer.

        Args:
            pathname (str): The current pathname.
            n_intervals (int): The number of intervals that have passed.

        Returns:
            dict: The updated style for the animation overlay.
        """
        ctx = dash.callback_context
        if not ctx.triggered:
            return {'display': 'none'}
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'url':
            return {'display': 'block', 'position': 'fixed', 'top': '0', 'left': '0', 'width': '100%', 'height': '100%', 'background': 'rgba(255, 255, 255, 0.8)', 'z-index': '9999'}
        elif trigger_id == 'animation-timer':
            return {'display': 'none'}
        return {'display': 'none'}

    def render_page_content(self, pathname):
        """
        Render the page content based on the current pathname.

        Args:
            pathname (str): The current pathname.

        Returns:
            Div: The content to be rendered.
        """
        if pathname == '/':
            return layouts.home_layout
        elif '/product-analysis' in pathname:
            if 'region:' in pathname:
                region_name = pathname.split('region:')[1]
                Region = region_name
            return layouts.regional_layout
        elif '/market-analysis' in pathname:
            return layouts.district_layout
        return html.Div([
            html.H1('404: Not found', className='text-danger'),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised...")
        ])

app = VisualizationApp()

@application.callback(Output("modal", "is_open"), [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")], [State("modal", "is_open")])
def toggle_modal(n1, n2, is_open):
    return app.toggle_modal(n1, n2, is_open)

@application.callback(Output('cytoscape', 'elements'), Input('open-modal', 'n_clicks'), prevent_initial_call=True)
def update_elements(n_clicks):
    return app.update_elements(n_clicks)

@application.callback(Output('region-click-info', 'children'), [Input('crop-filter', 'value'), Input('region-filter', 'value'), Input('indicator-filter', 'value'), Input('date-slider', 'value'), Input('map', 'clickData')])
def display_region_click_info(crop_search, region_search, indicator_search, start_date, clickData):
    return app.display_region_click_info(crop_search, region_search, indicator_search, start_date, clickData)

@application.callback([Output('line-chart', 'figure'), Output('map', 'figure'), Output('region-filter', 'value')],
    [Input('url', 'pathname'), Input('crop-filter', 'value'), Input('region-filter', 'value'), Input('indicator-filter', 'value'),
    Input('date-slider', 'value'), Input('map', 'clickData'), Input('last-clicked-region', 'children')],
    [State('region-filter', 'value')])
def update_graph_and_dropdown(url, crop_search, region_search, indicator_search, start_date, clickData, last_clicked_region, current_region_search):
    return app.update_graph_and_dropdown(url, crop_search, region_search, indicator_search, start_date, clickData, last_clicked_region, current_region_search)

@application.callback(Output('product-sales-distribution', 'figure'),
    [Input('product-sales-range-slider', 'value'), Input('crop-filter', 'value'), Input('region-filter', 'value'),
    Input('indicator-filter', 'value'), Input('date-slider', 'value'), Input('last-clicked-region', 'children'),
    Input('map', 'clickData'), Input('url', 'pathname')])
def update_regional_analysis(sales_range, crop_search, region_search, indicator_search, start_date, last_clicked_region, clickData, url):
    return app.update_regional_analysis(sales_range, crop_search, region_search, indicator_search, start_date, last_clicked_region, clickData, url)

@application.callback(Output('market-sales-by-country', 'figure'),
    [Input('market-country-dropdown', 'value'), Input('crop-filter', 'value'), Input('region-filter', 'value'),
    Input('indicator-filter', 'value'), Input('date-slider', 'value'), Input('last-clicked-region', 'children'),
    Input('map', 'clickData')])
def update_district_analysis(selected_countries, crop_search, region_search, indicator_search, start_date, last_clicked_region, clickData):
    return app.update_district_analysis(selected_countries, crop_search, region_search, indicator_search, start_date, last_clicked_region, clickData)

@application.callback([Output('Header_text', 'children'), Output('Subheader_text', 'children')], [Input('url', 'pathname')])
def update_text(url):
    return app.update_text(url)

@application.callback(Output('animation-overlay', 'style'), [Input('url', 'pathname'), Input('animation-timer', 'n_intervals')])
def update_animation_style(pathname, n_intervals):
    return app.update_animation_style(pathname, n_intervals)

@application.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    return app.render_page_content(pathname)
