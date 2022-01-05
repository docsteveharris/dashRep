
"""
Placeholder for ED
"""
from dash import dash_table as dt
from dash import dcc, html

from wrangle import sitrep as wng
from config.config import ConfigFactory

conf = ConfigFactory.factory()


ed = html.Div([
    html.H1('Emergency Department data'),
    html.P('Page under construction'),
])

