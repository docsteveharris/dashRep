import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__,
                external_stylesheets=[
                    dbc.themes.FLATLY,
                    dbc.icons.FONT_AWESOME,
                ],
                suppress_callback_exceptions=True)
server = app.server
