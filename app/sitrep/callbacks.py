"""
Functions (callbacks) that provide the functionality
"""
import json
import numpy as np
import pandas as pd

import plotly.graph_objects as go

import dash
import dash_daq as daq
from dash import Dash, Input, Output, State
from dash import dash_table as dt
import dash_bootstrap_components as dbc
from dash import dcc, html

from app import app
from wrangle import sitrep as wng
from utils import utils
from config.config import ConfigFactory, footer, header, nav

conf = ConfigFactory.factory()

def count_beds_in_ward_skeleton(ward):
    df_skeleton = wng.get_bed_skeleton(ward, conf.SKELETON_DATA_SOURCE, dev=conf.DEV)
    return df_skeleton.shape[0]


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
    df_user = wng.get_user_data('sitrep_edits', conf.USER_DATA_SOURCE, dev=conf.DEV_USER)
    # merge in 'empty beds' using the reported skeleton
    df_skeleton = wng.get_bed_skeleton(ward, conf.SKELETON_DATA_SOURCE, dev=conf.DEV)
    df_orig = wng.merge_hylode_user_data(df_skeleton, df_clean, df_user)
    # data wrangling
    df = wng.wrangle_data(df_orig, conf.COLS)
    return df


@app.callback(
    output=dict(json_data=Output("source-data", "data")),  # output data to store
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
        # collect the data from source
        dfo = request_data(ward)
        # collect the data from the displayed datatable
        dfn = pd.DataFrame.from_records(dfjson)
        # compare
        df_edits = utils.tbl_compare(dfo, dfn, cols2save=['wim_1', 'discharge_ready_1_4h'], idx=['ward_code', 'mrn'])
        if df_edits.shape[0]:
            print(df_edits)
            # TODO: write function to save updates to database or file store (i.e. user data)
            wng.write_data(df_edits, 'sitrep_edits', conf.USER_DATA_SOURCE)
            # then re-rerun request_data which should now bring in fresh 'user data'
            # return this
            df = request_data(ward)
        else:
            print("***WARNING: No edits found to save")
            # return just the original data
            df = dfo

        # TODO: write function to replay updates onto original
        # this should be part of the 'read data in' i.e. just uses the existing 'merge user' functionality

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
    # TODO: can you highlight using colour those fields that are edited but not saved
    for i, row in enumerate(rows):
        if i == 2:
            print(row)
    return rows


@app.callback(
    Output("datatable-main", "children"),
    Input("source-data", "data"),
    State("icu_active", "data"),
)
def gen_datatable_main(json_data, icu):
    print(f"Working with {icu}")

    # datatable defined by columns and by input data
    # abstract this to function so that you can guarantee the same data each time

    COL_DICT = [
        {"name": v, "id": k} for k, v in conf.COLS.items() if k in conf.COLS_FULL
    ]

    # prepare properties of columns
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


@app.callback(
    Output("gauge_occupancy", "children"),
    Input("source-data", "data"),
    Input("icu_active", "data"),
    )
def gauge_occupancy(json_data, ward):
    """
    Generates the graduated bar summarising current occupancy

    :param      json_data:  json representation of the current dataframe
    :type       json_data:  { type_description }
    """
    df = pd.DataFrame.from_records(json_data)
    occ_max = count_beds_in_ward_skeleton(ward)

    occ = df.mrn.count()
    occ_scaled = occ / occ_max * 10

    res = daq.GraduatedBar(
        color={
            "gradient": True,
            "ranges": {"green": [0, 4], "yellow": [4, 7], "red": [7, 10]},
        },
        showCurrentValue=True,
        # vertical=True,
        value=occ_scaled,
    )

    return res


@app.callback(
    Output("gauge_work", "children"),
    Input("source-data", "data"),
    Input("icu_active", "data"),
    )
def gauge_work(json_data, ward):
    """
    Generates the graduated bar summarising current work intensity
    Assumes the max possible is ?5x the number number of beds

    :param      json_data:  json representation of the current dataframe
    :type       json_data:  { type_description }
    """
    df = pd.DataFrame.from_records(json_data)

    wim_max = count_beds_in_ward_skeleton(ward) * 4
    wim_sum = df["wim_1"].sum()
    wim_sum_scaled = wim_sum / wim_max * 10

    res = daq.GraduatedBar(
        color={
            "gradient": True,
            "ranges": {"green": [0, 4], "yellow": [4, 7], "red": [7, 10]},
        },
        showCurrentValue=True,
        # vertical=True,
        value=wim_sum_scaled,
    )

    return res


    occ = df.mrn.count()
    occ_scaled = occ / occ_max * 10

    res = daq.GraduatedBar(
        color={
            "gradient": True,
            "ranges": {"green": [0, 4], "yellow": [4, 7], "red": [7, 10]},
        },
        showCurrentValue=True,
        # vertical=True,
        value=occ_scaled,
    )

    return res
