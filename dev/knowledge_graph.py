import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc

# Node names and their updated paddy tonnage with increased variance
node_tonnage = {
    "Union de Ndelle": 100, "Miller de Union de Ndelle 8": 150,
    "Union de Ndiaye": 180, "Miller de Union de Ndiaye 8": 160,
    # Add the rest of your nodes similarly
}

# Function to determine node size based on tonnage
def calculate_node_size(tonnage):
    base_size = 15  # Minimum size
    return base_size + tonnage / 10  # Scaling factor

# Function to determine edge width based on tonnage
def calculate_edge_width(u_tonnage, v_tonnage):
    avg_tonnage = (u_tonnage + v_tonnage) / 2
    base_width = 1  # Minimum width
    return base_width + avg_tonnage / 100  # Scaling factor

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Button("Show Graph", id="open-modal", n_clicks=0),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Knowledge Graph")),
            dbc.ModalBody(
                cyto.Cytoscape(
                    id='cytoscape',
                    elements=[],
                    layout={'name': 'breadthfirst'},
                    style={'width': '100%', 'height': '500px'},
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(label)',
                                'width': 'data(weight)',
                                'height': 'data(weight)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'background-color': '#6495ED'
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 'data(width)',
                                'line-color': '#FFD700',
                                'target-arrow-color': '#FFD700',
                                'target-arrow-shape': 'triangle'
                            }
                        }
                    ]
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
            ),
        ],
        id="modal",
        is_open=False,
        size="lg",
    )
])

@app.callback(
    Output("modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("modal", "is_open")]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('cytoscape', 'elements'),
    Input('open-modal', 'n_clicks'),
    prevent_initial_call=True
)
def update_elements(n_clicks):
    if n_clicks > 0:
        # Generate nodes and edges when the modal is opened
        nodes = [
            {
                'data': {'id': name, 'label': f'{name} ({tonnage} tonnes)', 'weight': calculate_node_size(tonnage)},
                'classes': 'top-center'
            } for name, tonnage in node_tonnage.items()
        ]

        edges = [
            {'data': {'source': u, 'target': v, 'width': calculate_edge_width(node_tonnage[u], node_tonnage[v])}}
            for u, v in [
                ("Union de Ndelle", "Miller de Union de Ndiaye 8"),
                # Add the rest of your edges similarly
            ]
        ]

        elements = nodes + edges
        return elements
    return []

if __name__ == '__main__':
    app.run_server(debug=True)
