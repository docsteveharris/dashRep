from collections import OrderedDict
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
import numpy as np

import plotly.graph_objects as go

import dash
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

from data_mx import read_data, wrangle_data, write_data, prep_cols_for_table

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8051

DATA_SOURCE = Path('../data/icu.json')
COLS = OrderedDict({
    'ward_code': 'Ward',
    'bed_code': 'Bed',

    'admission_dt': 'Admission',

    'mrn': 'MRN',
    'name': 'Full Name',
    'admission_age_years': 'Age',
    'sex': 'Sex',
    'dob': 'DoB',

    'wim_1': 'Work Intensity',
    'wim_r': 'Work Reported',
})


# # TODO: this needs to be created on the fly from the data table not from the df
# fig = go.Figure(data=go.Scatterpolar(
#     r=df.wim_1.to_list(),
#     theta=df.admission_age_years.to_list(),
#     mode='markers',
# ))

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


app.layout = dbc.Container([
    dbc.Alert('Wow! A data table in the browser'),
    dbc.Label('Click a cell in the table to watch it turn red!!'),

    dcc.Interval(id='interval_data', interval=60 * 60 * 1000, n_intervals=0),
    html.Div(id='datatable'),

    # dbc.Alert(['Update work reported? ',
    #            dcc.Input(id='active-cell-value',
    #                      type='number',
    #                      debounce=False)],
    #           color='info'),

    # dcc.Graph(id='fig1', figure=fig),

])


@app.callback(Output('datatable', 'children'),
              Input('interval_data', 'n_intervals'))
def gen_datatable(df):
    global DATA_SOURCE
    global COLS
    df_orig = read_data(DATA_SOURCE)
    df = wrangle_data(df_orig, COLS)
    return [
        dt.DataTable(
            id='tbl',
            columns=prep_cols_for_table(df, COLS),
            data=df.to_dict('records'),

            editable=False,

            style_cell={'padding': '5px'},
            style_cell_conditional=[
                {
                    'if': {'column_id': 'name'},
                    'textAlign': 'left'
                }
            ],
            style_table={'overflowX': 'auto'},

            filter_action='native',
            sort_action='native',
            page_size=10,
        ),
    ]


# @app.callback(
#     Output('tbl', 'data'),
#     Input('tbl', 'data_timestamp'),
#     [State('tbl', 'data'),
#      ])
# def update_table(timestamp, data):
#     df = read_data(DATA_SOURCE)
#     df = wrangle_data(df, COLS)
#     return df


# @app.callback(
#     # Output('tbl', 'data'),
#     Input('active-cell-value', 'value'),
#     [State('tbl', 'data'), State('tbl', 'active_cell')])
# def update_work_reported(new_value, data, cell):
#     # if cell is None or new_value is None:
#     #     return data

#     col = cell['column_id']
#     row = cell['row']
#     old_val = data[row][col]  # uses data to get value

#     # if old_val == new_value:
#     #     return data
#     # else:
#     data[row]['wim_r'] = new_value
#     write_data(data, DATA_SOURCE)
#     return data


# @app.callback(
#     Output('active-cell-value', 'value'),
#     Input('tbl', 'active_cell'),
#     State('tbl', 'data')
# )
# def active_cell_status(cell, data):
#     if not cell:
#         return None

#     col = cell['column_id']
#     row = cell['row']
#     val = data[row][col]  # uses data to get value

#     # msg = f"Cell ({cell['row']},{cell['column']}) with the value {val} has been selected"

#     return val


if __name__ == "__main__":
    app.run_server(
        port=SERVER_PORT,
        host=SERVER_HOST,
        debug=True
    )
