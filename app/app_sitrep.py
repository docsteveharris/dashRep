"""
Functions (callbacks) that provide the functionality
"""
import json

import dash
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

import utils
from app import app

conf = ConfigFactory.factory()


def request_data(ward):
    """
    Gets data from source system for the named ward
    
    :param      ward:  The ward
    :type       ward:  string
    """
    # prepare the URL and get the data as per sitrep API
    url_ward = wng.gen_hylode_url("sitrep", ward)
    df_ward = wng.get_hylode_data(url_ward, dev=conf.DEV_HYLODE)

    # prepare the URL and get the data as per census API
    url_census = wng.gen_hylode_url("census", ward)
    df_census = wng.get_hylode_data(url_census, dev=conf.DEV_HYLODE)

    # assume census API is correct and drop unmatched patients returned by sitrep
    df_clean = wng.merge_census_data(df_ward, df_census, dev=conf.DEV_HYLODE)

    # merge in user updates to data
    df_user = wng.get_user_data(conf.USER_DATA_SOURCE, dev=conf.DEV_USER)
    # merge in 'empty beds' using the reported skeleton
    df_skeleton = wng.get_bed_skeleton(ward, conf.SKELETON_DATA_SOURCE, dev=conf.DEV)
    df_orig = wng.merge_hylode_user_data(df_skeleton, df_clean, df_user)
    # data wrangling
    df = wng.wrangle_data(df_orig, conf.COLS)
    return df


@app.callback(
    output=dict(json_data=Output("table-data", "data")),  # output data to store
    inputs=dict(
        dfjson=State("tbl-main", "data"),
        ward=Input("icu_active", "data"),
        intervals=Input("interval-data", "n_intervals"),
        save_btn=Input("tbl-save", "n_clicks"),
        reset_btn=Input("tbl-reset", "n_clicks"),
    ),
    prevent_initial_call=True,  # suppress_callback_exceptions does not work
)
def data_io(dfjson, ward, save_btn, reset_btn, intervals):
    """
    stores the data in a dcc.Store
    runs on load and will be triggered each time the table is updated or the REFRESH_INTERVAL elapses
    kind of routes the load/save/reset actions
    """
    ctx = dash.callback_context
    trigger = ctx.triggered[0]
    print(trigger)
    ward = ward.lower()

    if trigger['prop_id'] == 'icu_active.data':
        print(f"***INFO: switching units to {ward}")
        df = request_data(ward)
    elif trigger['prop_id'] == 'tbl-reset.n_clicks':
        print(f"***INFO: resetting to initial data load")
        df = request_data(ward)
    elif trigger['prop_id'] == 'tbl-save.n_clicks':
        print(f"***INFO: CACHING data back to dash.Store")
        dfo = request_data(ward)
        # print(dfo.head())
        dfn = pd.DataFrame.from_records(dfjson)
        # print(dfn.head())
        df_edits = utils.tbl_compare(dfo, dfn, cols2save=['wim_1', 'discharge_ready_1_4h'], idx=['mrn'])
        print(df_edits)
        # TODO: write function to replay updates onto original
        # TODO: write function to save updates to database or file store
    else:
        raise NotImplementedError

    return dict(json_data=df.to_dict("records"))


@app.callback(
    Output("tbl-main", "data"),
    Input("tbl-main", "data_timestamp"),
    State("tbl-main", "data"),
    prevent_initial_call=True,  # suppress_callback_exceptions does not work
)
def update_table(timestamp, rows):
    for i, row in enumerate(rows):
        if i == 2:
            print(row)
    return rows


@app.callback(
    Output("datatable-main", "children"),
    Input("table-data", "data"),
    State("icu_active", "data"),
)
def gen_datatable_main(json_data, icu):
    print(f"Working with {icu}")
    COL_DICT = [
        {"name": v, "id": k} for k, v in conf.COLS.items() if k in conf.COLS_FULL
    ]

    # updates b/c list are mutable
    utils.deep_update(
        utils.get_dict_from_list(COL_DICT, "id", "wim_1"), dict(editable=True)
    )
    utils.deep_update(
        utils.get_dict_from_list(COL_DICT, "id", "discharge_ready_1_4h"),
        dict(editable=True),
    )
    utils.deep_update(
        utils.get_dict_from_list(COL_DICT, "id", "discharge_ready_1_4h"),
        dict(presentation="dropdown"),
    )

    DISCHARGE_OPTIONS = ["Ready", "No", "Review"]

    dto = (
        dt.DataTable(
            id="tbl-main",
            columns=COL_DICT,
            data=json_data,
            editable=False,
            dropdown={
                "discharge_ready_1_4h": {
                    "options": [{"label": i, "value": i} for i in DISCHARGE_OPTIONS],
                    "clearable": False,
                },
            },
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
                {"if": {"column_id": "discharge_ready_1_4h"}, "textAlign": "left"},
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
    )

    # wrap in container
    dto = [
        dbc.Container(
            dto,
            className="dbc",
        )
    ]
    return dto


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
                    className="dbc d-grid d-md-flex justify-content-md-end btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active btn-primary",
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
            className="dbc",
        ),
        # html.Div(id="which_icu"),
    ],
    className="radio-group",
)

save_reset_button = html.Div(
    [
        # dbc.ButtonGroup(
        # [
        dbc.Button(
            "Save", id="tbl-save", color="success", n_clicks=0, outline=False, size="md"
        ),
        dbc.Button(
            "Reset",
            id="tbl-reset",
            color="warning",
            n_clicks=0,
            outline=False,
            size="md",
        ),
        # ]
        # ),
    ],
)

# main page body currently split into two columns 9:3
main = dbc.Container(
    [
        # All unit content here plus unit selector
        dbc.Row(
            [
                dbc.Col([icu_radio_button], width={"offset": 6, "width": 4}),
                # dbc.Col( [ html.Div(id="which_icu"),], md=6 ),
                dbc.Col([save_reset_button], md=2),
            ],
            # className="g-0",
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
            align="start",
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
        # use this to table-data when the data changes
        dcc.Store(id="table-data"),
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
