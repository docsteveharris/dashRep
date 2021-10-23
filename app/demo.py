from collections import OrderedDict
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

import dash
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

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


# Read in the data
df = pd.read_json(DATA_SOURCE)

# Prep and wrangle
df['admission_dt'] = pd.to_datetime(
    df['admission_dt'], infer_datetime_format=True)
df['admission_dt'] = df['admission_dt'].dt.strftime("%H:%M %d %b %Y")
df = df[COLS.keys()]
df.sort_values(by='bed_code', inplace=True)


columns = [{"name": i, "id": i} for i in df.columns if i in COLS.keys()]
for column in columns:
    column['name'] = COLS[column['id']]
    if column['id'] == 'admission_dt':
        column['type'] = 'datetime'


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Alert('Wow! A data table in the browser'),
    dbc.Label('Click a cell in the table to watch it turn red!!'),
    dt.DataTable(
        id='tbl',
        columns=columns,
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

    dbc.Alert(['Update work reported? ',
               dcc.Input(id='active-cell-value',
                         type='number',
                         debounce=False)],
              color='warning'),
    dbc.Alert(html.Plaintext(id='store-text'), color='info'),


])


# @app.callback(
#     Output[])
# def active_cell_update_value():
#     #
# @app.callback(
#     Output('store-text', 'children'),
#     Input('signal', 'data')
# )
# def display_store(s):
#     return str(s)

@app.callback(
    Output('tbl', 'data'),
    Input('active-cell-value', 'value'),
    [State('tbl', 'data'), State('tbl', 'active_cell')])
def update_work_reported(new_value, data, cell):

    col = cell['column_id']
    row = cell['row']
    old_val = data[row][col]  # uses data to get value

    if old_val == new_value or new_value is None:
        return data
    else:
        data[row]['wim_r'] = new_value
        return data



@app.callback(
    Output('active-cell-value', 'value'),
    Input('tbl', 'active_cell'),
    State('tbl', 'data')
)
def active_cell_status(cell, data):
    if not cell:
        return 'No cell has been selected'

    col = cell['column_id']
    row = cell['row']
    val = data[row][col]  # uses data to get value

    # msg = f"Cell ({cell['row']},{cell['column']}) with the value {val} has been selected"

    return val


if __name__ == "__main__":
    app.run_server(debug=True)
