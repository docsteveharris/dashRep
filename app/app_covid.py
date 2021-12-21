"""
Display local COVID information
"""
import arrow
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import requests

from dash import Dash, Input, Output, State
from dash import dash_table as dt
from dash import dcc, html

from config import header, nav
from wrangle_govuk import HOSP_CASES
from app import app



@app.callback(Output("cases-hosp-ncl", "figure"), Input("gov_uk", "data"))
def cases_hosp_ncl(data):
    df = pd.DataFrame.from_records(data)
    df = df[df.inNCL01]
    trusts = df.areaCode.unique().tolist()
    fig = go.Figure()

    for trust in trusts:
        _df = df.loc[df.areaCode == trust]
        fig.add_trace(
            go.Scatter(
                name=_df.iloc[0].shortName,
                x=_df.date,
                y=_df.hospitalCases,
            )
        )
    return fig


@app.callback(Output("cases-hosp-london", "figure"), Input("gov_uk", "data"))
def cases_hosp_london(data):
    df = pd.DataFrame.from_records(data)
    df = df.groupby(['date', 'sectorName']).sum('hospitalCases').reset_index()
    sectors = df.sectorName.unique().tolist()

    fig = go.Figure()

    for sector in sectors:
        _df = df.loc[df.sectorName == sector]
        fig.add_trace(
            go.Scatter(
                name=sector,
                x=_df.date,
                y=_df.hospitalCases,
            )
        )
    return fig


@app.callback(Output("gov_uk", "data"), Input("interval-data", "n_intervals"))
def request_hosp_cases(n_intervals):
    """Prepared in wrangle_govuk"""
    df = HOSP_CASES
    return df.to_dict("records")


tab_hospital = dbc.Row(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3("North Central London", className="card-title"),
                    dcc.Graph(id="cases-hosp-ncl"),
                ]
            ),
            className="mt-3",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3("London sectors", className="card-title"),
                    dcc.Graph(id="cases-hosp-london"),
                ]
            ),
            className="mt-3",
        ),
    ]
)


main = dbc.Tabs(
    [
        dbc.Tab(tab_hospital, label="Hospital cases"),
    ]
)


dash_only = html.Div(
    [
        dcc.Interval(id="interval-data", interval=24 * 60 * 60 * 1000, n_intervals=0),
        dcc.Store(id="gov_uk"),
    ]
)


covid = dbc.Container(
    fluid=True,
    children=[
        header,
        nav,
        main,
        dash_only,
    ],
)
