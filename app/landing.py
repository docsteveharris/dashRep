"""
Menu and landing page
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from config import ConfigFactory
from config import header, nav, footer


main = html.Div([
    html.P('Welcome to the UCLH critical care sitrep and COVID tool')
])


landing = dbc.Container(
    fluid=True,
    children=[
        header,
        nav,
        main,
        footer,
        # dash_only,
    ],
)
