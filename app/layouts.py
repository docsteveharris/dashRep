import dash
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

import pandas as pd
import numpy as np

from config import ConfigFactory
conf = ConfigFactory.factory()

# a bright banner across the top of the page
header = html.Div(
    dbc.Row([
        dbc.Col(html.H1("Sitrep v2", className="bg-primary text-white p-2"), md=12),
    ])
)

# main page body currently split into two columns 9:3
main = html.Div(
    dbc.Row([
        # main space
        dbc.Col([
            html.Div(dcc.Graph(
                id='polar-main',
                config={
                    'responsive': True,
                    'autosizable': True,
                }
            )),
            html.P('Here is the polar plot')
        ], md=9),
        dbc.Col([
            # html.P('Here is patient list'),
            html.Div(id="datatable-side"),
        ], md=3),
    ])
)

# footer! mainly marking the end of the page
# but perhaps put the patient detail here
footer = html.Div(
    dbc.Row([
        dbc.Col(
            html.Div([
                html.P(id='msg'),
                html.P("Here is some detailed note held in the footer")
            ]), md=12),
    ])
)


# use this to store dash components that you don't need to 'see'
dash_only = html.Div([
    dcc.Interval(id="interval-data",
                 interval=conf.REFRESH_INTERVAL, n_intervals=0),
    # use this to signal when the data changes
    dcc.Store(id="signal"),
    dcc.Store(id="tbl-active-row"),
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
