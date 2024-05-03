from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from appflask import application

application = application
server = application.server
# Assuming layouts.py contains definitions for different page layouts
from layouts import home_layout, regional_layout, district_layout
from data import load_categories, load_data, load_regions_geojson


list_of_categories = load_categories()
#print("LIST OF CATEGORIES: ", list_of_categories)
# Customized Navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("RISO DATA", href="/", className="me-auto"),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("NATIONAL", href="/")),
                        dbc.NavItem(dbc.NavLink("REGIONAL", href="/product-analysis")),
                        dbc.NavItem(dbc.NavLink("DISTRICT", href="/market-analysis")),
                    ],
                    className="ms-auto",  # Margin start auto for right alignment in LTR languages
                    navbar=True,
                ),
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ],
        fluid=True,  # Use the full width of the screen for the navbar container
    ),
    color="dark",  # Dark theme navbar
    dark=True,  # Light text color for contrast
    className="mb-4",  # Margin bottom for spacing
    style={'position': 'fixed', 'top': 0, 'left': 0, 'right': 0, 'z-index': '1020'},  # Ensure it's always on top
)

# Adjust the main layout to add padding-top to the content
application.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', style={'margin-left': '25%', 'padding-top': '56px'}),  # Adjust padding-top based on the navbar height
    # Include the sidebar layout if necessary
])

# Product Market Fit

# Callback to toggle the collapse on small screens
@application.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
#

#Define the sidebar layout with interactive widgets
#list_values =list_of_categories["Culture"]
list_categories_specific = list_of_categories["REGION"]
sidebar = html.Div(
    [
        html.Div([html.Hr(), html.Hr(), html.Hr()], style={'background-color': '#343a40', 'padding': '2px'}),  # Enhanced visual separator
        
        html.P('Filter Data', className='lead', style={'color': '#FFFFFF', 'font-weight': 'bold', 'margin-bottom': '20px'}),  # Improved text styling
        
        html.P('Select the region you want to visualize', className='lead', style={'color': '#ADB5BD'}),  # Text color adjustment for better readability
        dcc.Dropdown(list_categories_specific, list_categories_specific, id="region-filter", multi=True, style={'background-color': '#495057', 'color': '#FFFFFF'}),  # Dropdown styling
        html.Br(),
        
        html.P('Select the time you want to visualize', className='lead', style={'color': '#ADB5BD'}),
        dbc.Row([dbc.Col(dcc.RangeSlider(id='date-slider', min=2016, max=2024, step=1, value=[2016, 2020], marks={i: str(i) for i in range(2016, 2024, 1)}, 
                                         className='px-3'), width=12)], className='mb-4', style={'padding': '10px', 'background-color': '#495057', 'border-radius': '5px'}),  # RangeSlider styling within a colored Row
        
        html.P('Select the crops you want to visualize', className='lead', style={'color': '#ADB5BD'}),
        dcc.Dropdown(list_of_categories["Culture"], list_of_categories["Culture"], id="crop-filter", multi=True, style={'background-color': '#495057', 'color': '#000'}),
        html.Div(id='last-clicked-region', style={'display': 'none'}),

        html.Br(),
        html.P('Select the metrics you want to visualize', className='lead', style={'color': '#ADB5BD'}),
        html.Div([html.Hr()], style={'background-color': '#343a40', 'padding': '2px'}),  # Enhanced visual separator
        dcc.Dropdown(list_of_categories["Indicateur"], 'Production en tonne', id="indicator-filter", style={'background-color': '#495057', 'color': '#000'}),
        html.Br(),
            dbc.Button('DOWNLOAD DATA ".CSV"  ', id='btn-nclicks-1', n_clicks=0,color="primary",outline=True),
            dbc.Button('DOWNLOAD DATA ".XLSX" ', id='btn-nclicks-2', n_clicks=0,color="primary",outline=True),
            dbc.Button('DOWNLOAD DATA ".H5  " ', id='btn-nclicks-3', n_clicks=0,color="primary",outline=True),
    ],
    style={'position': 'fixed', 'left': 0, 'top': 0, 'bottom': 0, 'width': '20%', 'padding': '20px', 'background-color': '#2f2f2f', "z-index": "30"}
)

# Main layout of the app that includes the sidebar
application.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    sidebar,  # Include the sidebar layout
    html.Div(id='page-content', style={'margin-left': '25%', 'padding-top': '56px'}),  # Adjusted padding-top for consistency with navbar height
])

# # Callback to update page content based on navigation
# @app.callback(
#     Output('page-content', 'children'),
#     [Input('url', 'pathname')]
# )
# def render_page_content(pathname):
#     if pathname == '/':
#         return home_layout
#     elif pathname == '/product-analysis':
#         return product_layout
#     elif pathname == '/market-analysis':
#         return market_layout
#     # Add more pages as needed
#     return html.P("404: Page not found")
import callbacks
if __name__ == '__main__':
    application.run_server(debug=True)

