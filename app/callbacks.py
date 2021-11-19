"""
Functions (callbacks) that provide the functionality
"""
import json
from app import app
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_daq as daq

import plotly.graph_objects as go

import pandas as pd
import numpy as np

import wrangle as wng
from config import ConfigFactory
conf = ConfigFactory.factory()


@app.callback(
    Output("datatable-patient", "children"),
    [Input("tbl-side-selection", "data"), Input("signal", "data"), ])
def gen_datatable_patient(row_id, json_data):
    """
    Draw the patient level data

    :param      row_id:  the row selected from the side datatable
    :param      data:        the patient data
    """
    # filter cols
    COL_NAMES = [{"name": v, "id": k}
                 for k, v in conf.COLS.items() if k in conf.COLS_FULL]

    # TODO: shouldn't need to do a roundtrip through a pandas dataframe
    # filter the json data by the selected table row
    df = pd.DataFrame.from_records(json_data)
    df = df[df['id'] == row_id]  # must use tbl id
    json_data = df.to_dict("records")

    return [
        dt.DataTable(
            id="tbl-patient",
            columns=COL_NAMES,
            data=json_data,
            editable=False
        )]


@app.callback(Output("datatable-side", "children"),
              [Input("signal", "data"), ])
def gen_datatable_side(json_data):
    COL_NAMES = [{"name": v, "id": k}
                 for k, v in conf.COLS.items() if k in conf.COLS_SIDEBAR]

    return [
        dt.DataTable(
            id="tbl-side",
            columns=COL_NAMES,
            data=json_data,
            editable=False,
            style_as_list_view=True,  # remove col lines
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
            style_data={'color': 'black', 'backgroundColor': 'white'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)'}
            ],
            sort_action="native",
            cell_selectable=False,
            row_selectable='single',
        ),
    ]


@app.callback(Output("polar-main", "figure"),
              [Input("tbl-side-selection", "data"), Input("signal", "data"), ])
def draw_fig_polar(row_id, data):
    """
    Draws a fig polar.

    :param      'data':  The data
    :type       'data':  { type_description }
    """

    df = pd.DataFrame.from_records(data)

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            name='',  # names the 'trace'
            theta=df["bed"],
            # log x+1 to avoid negative numbers
            marker_color=np.log(df["elapsed_los_td"]),
            r=df[["wim_1", "wim_r"]].max(axis=1),
            mode='markers+text',
            text=df["bed"],
            hovertemplate="WIM: %{r} Bed: %{theta}",
        )
    )

    # update layout
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))

    # update polar plot
    fig.update_polars(bgcolor='#FFF')
    fig.update_polars(hole=0.6)
    fig.update_polars(angularaxis_showgrid=True)
    fig.update_polars(angularaxis_gridcolor='#EEE')
    fig.update_polars(angularaxis_linecolor='grey')  # outer ring
    fig.update_polars(angularaxis_ticks='outside')
    fig.update_polars(angularaxis_direction='counterclockwise')
    fig.update_polars(radialaxis_showgrid=True)
    fig.update_polars(radialaxis_color='#999')
    fig.update_polars(radialaxis_gridcolor='#EEE')

    fig.update_traces(marker_line_color='rgba(0,0,0,1)')
    # fig.update_traces(marker_opacity=0.8)
    fig.update_traces(marker_size=20)
    fig.update_traces(hovertemplate="LoS: %{r} Bed: %{theta}")

    if row_id:
        dfi = df.reset_index(drop=True)
        row_num = dfi[dfi['id'] == row_id].index[0]
        row_nums = []
        row_nums.append(row_num)
        fig.update_traces(selectedpoints=row_nums,
                          selector=dict(type='scatterpolar'))
        fig.update_traces(selected_marker_size=40,
                          selector=dict(type='scatterpolar'))
        # fig.update_traces(selected_marker_opacity=1.0, selector=dict(type='scatterpolar'))
        fig.update_traces(selected_marker_color='red',
                          selector=dict(type='scatterpolar'))
        fig.update_traces(selected_textfont_color='white',
                          selector=dict(type='scatterpolar'))

    return fig


@app.callback(Output('occ-graduated-bar', 'children'),
              Input('signal', 'data'))
def gen_graduated_bar(json_data, occ_max=35):
    """
    Generates the graduated bar summarising current occupancy

    :param      json_data:  json representation of the current dataframe
    :type       json_data:  { type_description }
    """
    df = pd.DataFrame.from_records(json_data)

    occ = df.shape[0]
    occ_scaled = occ / occ_max * 10

    res = daq.GraduatedBar(
        color={"gradient": True, "ranges": {
            "green": [0, 4], "yellow": [4, 7], "red": [7, 10]}},
        showCurrentValue=True,
        # vertical=True,
        value=occ_scaled
    )

    return res


@app.callback(Output('wim-graduated-bar', 'children'),
              Input('signal', 'data'))
def gen_graduated_bar(json_data, wim_max=175):
    """
    Generates the graduated bar summarising current work intensity
    Assumes the max possible is ?5x the number number of beds

    :param      json_data:  json representation of the current dataframe
    :type       json_data:  { type_description }
    """
    df = pd.DataFrame.from_records(json_data)

    wim_sum = df[['wim_1', 'wim_r']].max(axis=1).sum()
    wim_sum_scaled = wim_sum / wim_max * 10

    res = daq.GraduatedBar(
        color={"gradient": True, "ranges": {
            "green": [0, 4], "yellow": [4, 7], "red": [7, 10]}},
        showCurrentValue=True,
        # vertical=True,
        value=wim_sum_scaled
    )

    return res


@app.callback(Output('msg', 'children'), [Input('tbl-side-selection', 'data'), ])
def gen_msg(active_row):
    if not active_row:
        res = """Click the table"""

    res = str(active_row)
    res = f"Selected row id is {res}"
    return res


@app.callback(Output('tbl-side-selection', 'data'),
              Input('tbl-side', 'derived_virtual_selected_row_ids'),
              State('signal', 'data')
              )
def get_datatable_side_selected_row(row_id, json_data):
    """
    returns the 'row_id' selected from the datatable (side bar)
    if nothing selected then returns the first row
    """
    if not row_id:
        row_id = json_data[0]['id']
    else:
        row_id = row_id[0]
    return row_id


# TODO n_intervals arg is unused but just ensures that store data updates
@app.callback(Output("signal", "data"), Input("interval-data", "n_intervals"))
def update_data_from_source(n_intervals):
    """
    stores the data in a dcc.Store
    runs on load and will be triggered each time the table is updated or the REFRESH_INTERVAL elapses
    """
    df_hylode = wng.get_hylode_data(
        conf.HYLODE_DATA_SOURCE, dev=conf.DEV_HYLODE)
    df_user = wng.get_user_data(conf.USER_DATA_SOURCE, dev=conf.DEV_USER)
    df_orig = wng.merge_hylode_user_data(df_hylode, df_user)
    df = wng.wrangle_data(df_orig, conf.COLS)
    return df.to_dict("records")
