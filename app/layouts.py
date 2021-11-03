import dash
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

import pandas as pd
import numpy as np

from config import ConfigFactory
conf = ConfigFactory.factory()

header = html.Div(
    dbc.Row([
        dbc.Col(html.H1("Sitrep v2", className="bg-primary text-white p-2"), md=12),
    ])
)

main = html.Div(
    dbc.Row([
        dbc.Col(html.P('Here is the polar plot'), md=9),
        dbc.Col([
            html.P('Here is patient list'),
            html.Div(id="datatable-side"),
            html.P('End of table')
        ], md=3),
    ])
)

footer = html.Div(
    dbc.Row([
        dbc.Col(html.P("Here is some detailed note held in the footer"), md=12),
    ])
)


dash_only = html.Div([
    dcc.Interval(id="interval-data", interval=conf.REFRESH_INTERVAL, n_intervals=0),
    # use this to signal when the data changes
    dcc.Store(id="signal"),
    dcc.Store(id="tbl-active-cell"),
])

# """Principal layout for sitrep2 page"""
sitrep = dbc.Container(
    fluid=True,
    children=[
        header,
        main,
        footer,
        dash_only,
    ]
)
