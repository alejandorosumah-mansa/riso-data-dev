import dash
import dash_bootstrap_components as dbc
from dash  import  html
import dash_extensions as de

external_stylesheets = [dbc.themes.BOOTSTRAP]

application = app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, "assets/style.css"], suppress_callback_exceptions=True)
server = application.server
url = "https://assets9.lottiefiles.com/packages/lf20_YXD37q.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))
# Create example app.
application.layout = html.Div(de.Lottie(options=options, width="25%", height="25%", url=url))
# The following line ensures that if you're running this file directly, it doesn't run the server.
# This line is optional and mainly used when deploying the app to a WSGI server.
if __name__ == "__main__":
    application.run_server(debug=True)
