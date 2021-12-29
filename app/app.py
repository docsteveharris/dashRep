"""
The application itself
"""
import dash
import dash_bootstrap_components as dbc


app = dash.Dash(
    __name__,
    title="HYLODE",
    update_title=None,
    external_stylesheets=[
        dbc.themes.MORPH,
        dbc.icons.FONT_AWESOME,
    ],
    suppress_callback_exceptions=True,
)
server = app.server
