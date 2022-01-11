"""
Placeholder for ED
"""
import json
import os
import warnings
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.config import ConfigFactory
from dash import dash_table as dt
from dash import dcc, html
from ridgeplot import ridgeplot
from wrangle import sitrep as wng

conf = ConfigFactory.factory()

# Extract the data
# TODO: wrap this in a function and then memoize it


def get_ed_data(dev=conf.DEV):
    if conf.DEV:
        df = pd.read_csv(
            "data/secret/ed_agg_30d_sample.csv", parse_dates=["extract_dttm"]
        )
    else:
        # Environment variables stored in conf.SECRETS
        # Construct the PostgreSQL connection
        uds_host = conf.SECRETS["EMAP_DB_HOST"]
        uds_name = conf.SECRETS["EMAP_DB_NAME"]
        uds_port = conf.SECRETS["EMAP_DB_PORT"]
        uds_user = conf.SECRETS["EMAP_DB_USER"]
        uds_passwd = conf.SECRETS["EMAP_DB_PASSWORD"]

        emapdb_engine = create_engine(
            f"postgresql://{uds_user}:{uds_passwd}@{uds_host}:{uds_port}/{uds_name}"
        )
        q = Path("notebooks/sql/ed.sql").read_text()
        df = pd.read_sql_query(q, emapdb_engine)

    return df


def tidy_ed_data(df):
    df["hour"] = df.extract_dttm.round("1H").dt.hour
    df["dow"] = df.extract_dttm.dt.dayofweek  # Monday = 0, Sunday = 6
    df["date"] = df.extract_dttm.round("1D").dt.date
    df["days"] = (
        (df.extract_dttm.max() - df.extract_dttm).round("1D").dt.days.astype(int)
    )
    df = df.loc[
        df.contrib == "All patients",
        [
            "extract_dttm",
            "days",
            "date",
            "dow",
            "hour",
            "num_adm_pred",
            "prob_this_num",
            "probs",
        ],
    ]
    return df


def filter_same(df, hour=True, dayofweek=True):
    """
    filters a dataframe by the same hour and/or day of week
    as the most recent data there

    :param      df:         { parameter_description }
    :type       df:         { type_description }
    :param      hour:       The hour
    :type       hour:       bool
    :param      dayofweek:  The dayofweek
    :type       dayofweek:  bool
    """
    # df0 : most recent measures
    df0 = df.loc[(df.extract_dttm == df.extract_dttm.max())]
    df0_hour = df0.iloc[0]["hour"]
    df0_dow = df0.iloc[0]["dow"]

    assert any([hour, dayofweek])
    if hour and dayofweek:
        res = df.loc[
            ((df.hour == df0_hour) & (df.dow == df0_dow)),
        ]
    elif hour:
        res = df.loc[
            df.hour == df0_hour,
        ]
    elif dayofweek:
        res = df.loc[
            df.dow == df0_dow,
        ]
    else:
        raise ValueError("One of hour or day of week must be selected")
    return res


def prepare_ridge_densities(df, xmax=40):
    # simplify dataframe
    dfr = df.loc[:, ["days", "num_adm_pred", "probs"]]
    # prepare a list of days in reverse order
    days = dfr.days.unique()
    days = days[np.argsort(-days)]

    # prepare a skeleton array structure
    num_adm_max = dfr.num_adm_pred.max()
    skeleton = pd.DataFrame(dict(num_adm_pred=range(num_adm_max)))
    ll = []

    for day in days:
        tt = dfr.loc[dfr.days == day].drop(["days"], axis=1)
        tt = pd.merge(skeleton, tt, how="left")
        tt = tt.reset_index(drop=True)
        tt = tt.loc[
            :xmax,
        ]
        tt = tt.values.transpose()
        ll.append(tt)
    res = np.asarray(ll)
    return days, res


def gen_ridgeplot(densities, labels):
    fig = ridgeplot(
        densities=densities,
        labels=labels,
        colorscale="portland",
        colormode="mean-minmax",
        spacing=1 / 5,
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(autosize=False, width=800, height=400)
    fig.update_layout(
        xaxis_title="Inpatient bed demand",
        yaxis_title="Predictions from days past<br>(i.e. up to 28 days ago)",
    )
    fig.update_layout(template="plotly_white")
    return fig


df = get_ed_data(dev=conf.DEV)
df = tidy_ed_data(df)
df = filter_same(df)
labels, densities = prepare_ridge_densities(df)
fig = gen_ridgeplot(densities, labels)


ed = html.Div(
    [
        html.H1("Emergency Department data"),
        html.P("Page under construction"),
        html.Div([dcc.Graph(figure=fig)]),
    ]
)
