
"""
Display local COVID information
"""
import pandas as pd
import requests
import arrow

from dash import dash_table as dt
from dash import dcc, html
from dash import Dash, Input, Output, State

import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from config import header, nav

from app import app

UCLH_LOCAL_TRUSTS = ['RAL', 'RAP', 'RKE', 'RRP', 'RRV']

@app.callback(
    Output("uclh-cases", "figure"),
    Input('gov_uk', 'data')
)
def covid_scatter(data):
    df = pd.DataFrame.from_records(data)
    fig = go.Figure()

    for trust in UCLH_LOCAL_TRUSTS:
        _df = df.loc[df.areaCode==trust]
        fig.add_trace(
            go.Scatter(
                name=_df.iloc[0].areaName,
                x=_df.date,
                y=_df.hospitalCases,
                ))

    return fig

@app.callback(Output("gov_uk", "data"), Input("interval-data", "n_intervals"))
def request_covid_data(n_intervals):
    # Import COVID information as per the gov.uk API here
    # All hospitals
    yesterday = str(arrow.now().shift(days=-1).format('YYYY-MM-DD'))
    url = f"https://coronavirus.data.gov.uk/api/v2/data?areaType=nhsTrust&release={yesterday}&metric=hospitalCases&format=json"
    response = requests.get(url)
    df = pd.json_normalize(response.json(), record_path='body')
    df = df[df.areaCode.isin(UCLH_LOCAL_TRUSTS)]
    df['date'] = pd.to_datetime(df['date'])
    return df.to_dict("records")



main = html.Div(dcc.Graph(id="uclh-cases"))

dash_only = html.Div([
        dcc.Interval(id="interval-data", interval = 24 * 60 * 60 * 1000, n_intervals=0),
        dcc.Store(id="gov_uk")
        ])


covid = dbc.Container(
    fluid=True,
    children=[
    header,
    nav,
    main,
    dash_only,
    ],
)
