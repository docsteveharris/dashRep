"""
Display local COVID information
"""
import arrow
import datetime
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from config import header, nav
from dash import Dash, Input, Output, State
from dash import dash_table as dt
from dash import dcc, html
from wrangle_govuk import CASES_BY_AGE, HOSP_CASES

from app import app


@app.callback(Output("cases-popn-age2d", "figure"), Input("cases-popn", "data"))
def cases_popn_age(data):
    df = pd.DataFrame.from_records(data)
    df['date'] = pd.to_datetime(df['date'])

    age_bands = df.age.unique().tolist()
    age_bands = list(set(age_bands) - set(["60+", "00_59", "unassigned"]))
    dff = df.loc[df.age.isin(age_bands) & (df.date > datetime.datetime.utcnow() - datetime.timedelta(days=365+31))]

    fig = px.density_heatmap(
        dff,
        x="date",
        y="age",
        z="cases",
        histfunc="sum",
        nbinsx=365+31,
        color_continuous_scale="Hot",
    )
    return fig


@app.callback(Output("cases-popn-age", "figure"), Input("cases-popn", "data"))
def cases_popn_age(data):
    df = pd.DataFrame.from_records(data)
    age_bands = df.age.unique().tolist()
    age_bands = list(set(age_bands) - set(["60+", "00_59", "unassigned"]))
    fig = go.Figure()

    for age in age_bands:
        _df = df.loc[df.age == age]
        fig.add_trace(
            go.Scatter(
                name=age,
                x=_df.date,
                y=_df.cases,
            )
        )
    return fig


@app.callback(Output("cases-hosp-ncl", "figure"), Input("cases-hosp", "data"))
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


@app.callback(Output("cases-hosp-london", "figure"), Input("cases-hosp", "data"))
def cases_hosp_london(data):
    df = pd.DataFrame.from_records(data)
    df = df.groupby(["date", "sectorName"]).sum("hospitalCases").reset_index()
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


@app.callback(Output("cases-hosp", "data"), Input("interval-data", "n_intervals"))
def request_hosp_cases(n_intervals):
    """Prepared in wrangle_govuk"""
    df = HOSP_CASES
    return df.to_dict("records")


@app.callback(Output("cases-popn", "data"), Input("interval-data", "n_intervals"))
def request_popn_cases(n_intervals):
    """Prepared in wrangle_govuk"""
    df = CASES_BY_AGE
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

tab_popn = dbc.Row(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3(
                        "Population cases by age band (London)", className="card-title"
                    ),
                    dcc.Graph(id="cases-popn-age"),
                ]
            ),
            className="mt-3",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H3(
                        "as a heatmap for the last 13 months", className="card-title"
                    ),
                    dcc.Graph(id="cases-popn-age2d"),
                ]
            ),
            className="mt-3",
        ),
    ]
)

main = dbc.Tabs(
    [
        dbc.Tab(tab_hospital, label="Hospital cases"),
        dbc.Tab(tab_popn, label="Community cases"),
    ]
)


dash_only = html.Div(
    [
        dcc.Interval(id="interval-data", interval=24 * 60 * 60 * 1000, n_intervals=0),
        dcc.Store(id="cases-hosp"),
        dcc.Store(id="cases-popn"),
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
