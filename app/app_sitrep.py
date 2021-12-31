"""
Functions (callbacks) that provide the functionality
"""
import json

import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import wrangle as wng
from config import ConfigFactory, footer, header, nav
from dash import Dash, Input, Output, State
from dash import dash_table as dt
from dash import dcc, html

from app import app

conf = ConfigFactory.factory()


# TODO n_intervals arg is unused but just ensures that store data updates
@app.callback(
    Output("signal", "data"),
    [
        Input("interval-data", "n_intervals"),
        Input("icu_active", "data"),
    ],
)
def update_data_from_source(n_intervals, icu):
    """
    stores the data in a dcc.Store
    runs on load and will be triggered each time the table is updated or the REFRESH_INTERVAL elapses
    """
    icu = icu.lower()
    print(f"Updating data for {icu.upper()}")
    # prepare the URL
    url_icu = wng.gen_hylode_url("sitrep", icu)
    url_census = wng.gen_hylode_url("census", icu)

    df_sitrep = wng.get_hylode_data(url_icu, dev=conf.DEV_HYLODE)
    df_census = wng.get_hylode_data(url_census, dev=conf.DEV_HYLODE)
    df_hylode = wng.merge_census_data(df_sitrep, df_census, dev=conf.DEV_HYLODE)
    df_user = wng.get_user_data(conf.USER_DATA_SOURCE, dev=conf.DEV_USER)
    df_skeleton = wng.get_bed_skeleton(icu, conf.SKELETON_DATA_SOURCE, dev=conf.DEV)
    df_orig = wng.merge_hylode_user_data(df_skeleton, df_hylode, df_user)
    df = wng.wrangle_data(df_orig, conf.COLS)
    return df.to_dict("records")


@app.callback(
    Output("datatable-main", "children"),
    Input("signal", "data"),
    State("icu_active", "data"),
)
def gen_datatable_main(json_data, icu):
    print(f"Working with {icu}")
    COL_NAMES = [
        {"name": v, "id": k} for k, v in conf.COLS.items() if k in conf.COLS_FULL
    ]

    return [
        dbc.Container(
            dt.DataTable(
                id="tbl-main",
                columns=COL_NAMES,
                data=json_data,
                editable=False,
                # active_cell=True,
                # style_as_list_view=True,  # remove col lines
                style_cell={
                    "fontSize": 12,
                    # 'font-family':'sans-serif',
                    "padding": "3px",
                },
                style_cell_conditional=[
                    {"if": {"column_id": "bay"}, "textAlign": "right"},
                    {"if": {"column_id": "bed"}, "textAlign": "left"},
                    {"if": {"column_id": "name"}, "textAlign": "left"},
                    {"if": {"column_id": "name"}, "fontWeight": "bolder"},
                ],
                style_data={"color": "black", "backgroundColor": "white"},
                # striped rows
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(220, 220, 220)",
                    }
                ],
                sort_action="native",
                cell_selectable=True,  # possible to click and navigate cells
                # row_selectable="single",
            ),
            # className="dbc",
        )
    ]


@app.callback(Output("icu_active", "data"), Input("icu_radio", "value"))
def store_icu_active(value):
    print(f"Storing active ICU as {value.lower()}")
    return value.lower()


@app.callback(Output("which_icu", "children"), Input("icu_active", "data"))
def display_icu_active(value):
    return html.H3(f"You are inspecting {value.upper()}")


"""
Layouts organised for sitrep
- header (from config)
- nav (from config)
- main
- footer (from config)
- dash_only (to store non visible parts of the app)
"""

icu_radio_button = html.Div(
    [
        html.Div(
            [
                dbc.RadioItems(
                    id="icu_radio",
                    className="d-grid d-md-flex justify-content-md-end btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-info",
                    labelCheckedClassName="active btn-info",
                    options=[
                        {"label": "T03", "value": "T03"},
                        {"label": "T06", "value": "T06"},
                        {"label": "GWB", "value": "GWB"},
                        {"label": "WMS", "value": "WMS"},
                        {"label": "NHNN", "value": "NHNN"},
                    ],
                    value="T03",
                )
            ],
        ),
        # html.Div(id="which_icu"),
    ],
    className="radio-group",
)


# main page body currently split into two columns 9:3
main = dbc.Container(
    [
        # All unit content here plus unit selector
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(id="which_icu"),
                        # html.I(className="fa fa-lungs-virus"),
                    ],
                    width={"order": "first", "width": True},
                ),
                dbc.Col([icu_radio_button], width={"order": "last", "width": "auto"}),
            ],
            justify="between",
        ),
        # Unit specific content here
        dbc.Row(
            [
                dbc.Col(
                    [html.Div(id="datatable-main")],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Ward aggregate details"),
                                        dbc.CardBody("CardBody"),
                                        dbc.CardFooter("CardFooter"),
                                    ]
                                ),
                            ],
                            align="start",
                        ),
                        dbc.Row(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Patient specific details"),
                                        dbc.CardBody("CardBody"),
                                        dbc.CardFooter("CardFooter"),
                                    ]
                                ),
                            ],
                            align="end",
                        ),
                    ],
                    md=6,
                ),
            ],
            align="end",
        ),
    ],
    fluid=True,
    # className="dbc",
)


# use this to store dash components that you don't need to 'see'
dash_only = html.Div(
    [
        dcc.Interval(id="interval-data", interval=conf.REFRESH_INTERVAL, n_intervals=0),
        # which ICU?
        dcc.Store(id="icu_active"),
        # use this to signal when the data changes
        dcc.Store(id="signal"),
        # dcc.Store(id="tbl-active-row"),
        dcc.Store(id="tbl-side-selection"),
    ]
)

# """Principal layout for sitrep2 page"""
sitrep = dbc.Container(
    fluid=True,
    className="dbc",
    children=[
        header,
        nav,
        main,
        footer,
        dash_only,
    ],
)
