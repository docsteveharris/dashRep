
"""
Display local COVID information
"""
import pandas as pd
import requests

from dash import dash_table as dt
from dash import dcc, html
from dash import Dash, Input, Output, State

import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from app import app


@app.callback(
    Output("uclh-cases", "figure"),
    Input('gov_uk', 'data')
)
def covid_scatter(data):
    df = pd.DataFrame.from_records(data)
    fig = go.Figure()

    _df = df.loc[df.areaCode=='RRV']
    fig.add_trace(
        go.Scatter(
            name='UCLH',
            x=_df.date,
            y=_df.hospitalCases,
            ))

    _df = df.loc[df.areaCode=='RAP']
    fig.add_trace(
        go.Scatter(
            name='North Mid',
            x=_df.date,
            y=_df.hospitalCases,
            ))
    return fig

@app.callback(Output("gov_uk", "data"), Input("interval-data", "n_intervals"))
def request_covid_data(n_intervals):
    # Import COVID information as per the gov.uk API here
    trust_codes = ['RRV', 'RAP']
    dfs = []
    for i, t in enumerate(trust_codes):
        url = f"https://api.coronavirus.data.gov.uk/v2/data?areaType=nhsTrust&areaCode={t}&metric=hospitalCases&format=json"
        response = requests.get(url)
        df = pd.json_normalize(response.json(), record_path='body')
        df['date'] = pd.to_datetime(df['date'])
        dfs.append(df)
    df = pd.concat(dfs)
    return df.to_dict("records")




covid = dbc.Container(
    fluid=True,
    children=[
    # html.Div(covid_datatable)
    html.Div(dcc.Graph(id="uclh-cases")),
    html.Div([
        dcc.Interval(id="interval-data", interval = 24 * 60 * 60 * 1000, n_intervals=0),
        dcc.Store(id="gov_uk")
        ]),
    ],
)
