import dash
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

import pandas as pd
import numpy as np

from config import Config


def layout_text_card():
    """Title and text at the top of the page"""
    return dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("SitRep Dashboard", className="card-title"),
                        html.H4("v2 (Dash)", className="card-subtitle"),
                        html.Div(
                            [
                                html.P(
                                    """Plot below is for T3 beds; radius is the 'work intensity', and colour is the elapased LoS!""",
                                    className="card-text",
                                )
                            ]
                        ),
                    ]
                )
            , color='secondary',
            # style={'width': '888rem'}
            className="w-50"
        )


def layout_new_value():
    """Data entry box for editing values selected from the table"""
    return html.Div(
        dbc.Card(
            dbc.CardBody(
                    html.Div(
                        [
                            dbc.Label('Click a WIM cell to update'),
                            dbc.Input(id="new-value", type="number", min=0, max=10),
                            # dbc.FormText('Type into the box above'),
                            dbc.Button( id="submit-button", n_clicks=0, children="Submit"),
                        ]
                    ),
            ),
        color='info')
    )


def layout_fig_polar():
    """Polar plot showing ward layout"""
    return html.Div(
        dcc.Graph(
            id="fig-polar",
            # style={'width': '500px'},
            config={
                "responsive": True,
                "autosizable": True,
            },
        ),
        # md=6
    )

sitrep = dbc.Container(
    [
        dbc.Row(
            [
                dbc.CardGroup([
                    layout_text_card(),
                    layout_new_value(),
                ])
            ]
        ),
        dbc.Alert(id="active-cell-value"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(layout_fig_polar()),
                dbc.Col(html.Div(id="datatable"), width=7)]
        ),
        html.Br(),
        # dbc.Alert(layout_new_value(), color="info"),
        dcc.Interval(id="interval-data", interval=Config.REFRESH_INTERVAL, n_intervals=0),
        # use this to signal when the data changes
        dcc.Store(id="signal"),
        dcc.Store(id="tbl-active-cell"),
    ],
    fluid=True
)


hello = dbc.Container([
    html.P('Hello World')])
