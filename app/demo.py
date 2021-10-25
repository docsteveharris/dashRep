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

import data_mx as dmx

HYLODE_DATA_SOURCE = '../data/icu.json'
USER_DATA_SOURCE = '../data/user_edits.csv'

DEV_HYLODE = True
DEV_USER = True

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8009

REFRESH_INTERVAL = 60 * 1000  # milliseconds

HYLODE_DATA_SOURCE = Path('../data/icu.json')
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
COL_NAMES = [{"name": v, "id": k} for k, v in COLS.items()]


# # TODO: this needs to be created on the fly from the data table not from the df
# fig = go.Figure(data=go.Scatterpolar(
#     r=df.wim_1.to_list(),
#     theta=df.admission_age_years.to_list(),
#     mode='markers',
# ))

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.config.suppress_callback_exceptions = True


app.layout = dbc.Container([
    html.P("""Click a cell in the table to watch it turn red!!"""),
    html.P("""Then update the selected value in the box below and it will be saved as 'Work Reported'"""),
    dbc.Alert(id='active-cell-value'),
    dbc.Alert(
        html.Div([
            dcc.Input(id='new-value',
                      type='number'),
            html.Button(id='submit-button', n_clicks=0, children='Submit')
        ]),
        color='info'),

    # dbc.Alert(['Update work reported? ',
    #            dcc.Input(id='active-cell-value',
    #                      type='number',
    #                      debounce=False)],
    #           color='info'),

    # dcc.Graph(id='fig1', figure=fig),
    
    html.Div(id='datatable'),

    dcc.Interval(id='interval-data', interval=REFRESH_INTERVAL, n_intervals=0),
    # use this to signal when the data changes
    dcc.Store(id='signal'),

    dcc.Store(id='tbl-active-cell')

])


@app.callback(Output('datatable', 'children'),
              [Input('signal', 'data')]
              )
def gen_datatable(json_data):
    global COL_NAMES
    return [
        dt.DataTable(
            id='tbl',
            columns=COL_NAMES,
            data=json_data,

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
            # TODO: does not work with paginated tables
            # page_size=10,
        ),
    ]


@app.callback(
    Output('new-value', 'value'),
    Input('tbl', 'active_cell'),
    State('tbl', 'data')
)
def update_input_default(cell, data):
    """Updates the default value for the user input"""
    if cell:
        col = cell['column_id']
        row = cell['row']
        val = data[row][col]  # uses data to get value
    else:
        val = None
    return val


@app.callback(
    Output('tbl-active-cell', 'data'),
    Input('tbl', 'active_cell'),
)
def update_active_cell_store(cell):
    """Stores the active cell dictionary so available to other components"""
    if cell:
        return cell


@app.callback(
    Output('active-cell-value', 'children'),
    Input('tbl-active-cell', 'data'),
    State('tbl', 'data')
)
def active_cell_status(cell, data) -> str:
    """Banner reporting which cell was selected"""
    if not cell:
        return 'No cell selected!'

    col = cell['column_id']
    row = cell['row']
    val = data[row][col]  # uses data to get value

    msg = f"Cell ({cell['row']},{cell['column']}) with the value {val} has been selected"

    return msg


@app.callback(Output('interval-data', 'n_intervals'),  # reset the interval timer?
              [Input('submit-button', 'n_clicks')],
              [State('new-value', 'value'),
               State('signal', 'data'),
               State('tbl-active-cell', 'data')
               ])
def update_value(n_clicks, new_value, data, cell):
    """
    writes the data back to the original data source
    this in turn then triggers the data table to reload
    """
    global HYLODE_DATA_SOURCE

    if cell:
        col = cell['column_id']
        row = cell['row']
        val = data[row][col]  # uses data to get value

    if n_clicks > 0:
        df = pd.DataFrame.from_records(data)

        df.loc[row, 'wim_r'] = new_value
        dmx.write_data(df, HYLODE_DATA_SOURCE)
    return 0


# TODO n_intervals arg is unused but just ensures that store data updates
@app.callback(Output('signal', 'data'),
              Input('interval-data', 'n_intervals'))
def update_data_from_source(n_intervals):
    """
    stores the data in a dcc.Store
    runs on load and will be triggered each time the table is updated or the REFRESH_INTERVAL elapses
    """
    global HYLODE_DATA_SOURCE
    global COLS
    df_hylode = dmx.get_hylode_data(HYLODE_DATA_SOURCE, dev=DEV_HYLODE)
    df_user = dmx.get_user_data(USER_DATA_SOURCE, dev=DEV_USER)
    df_orig = dmx.merge_hylode_user_data(df_hylode, df_user)
    df = dmx.wrangle_data(df_orig, COLS)
    return df.to_dict('records')


if __name__ == "__main__":
    app.run_server(
        port=SERVER_PORT,
        host=SERVER_HOST,
        debug=True
    )
