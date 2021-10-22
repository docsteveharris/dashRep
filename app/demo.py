from collections import OrderedDict
from pathlib import Path

import pandas as pd

import dash
from dash import Dash, Input, Output, callback
from dash import dash_table as dt
import dash_bootstrap_components as dbc

DATA_SOURCE = Path('../data/icu.json')
# TODO convert to ordered dictionary
COLS = OrderedDict({
    'ward_code': 'Ward',
    'bed_code': 'Bed',

    'admission_dt': 'Admission',

    'mrn': 'MRN',
    'name': 'Full Name',
    'admission_age_years': 'Age',
    'sex': 'Sex',
    'dob': 'DoB',

    'wim_1': 'Work Intensity'})



# Read in the data
df = pd.read_json(DATA_SOURCE)

# Prep and wrangle
df['admission_dt'] = pd.to_datetime(df['admission_dt'], infer_datetime_format=True)
df['admission_dt'] = df['admission_dt'].dt.strftime("%H:%M %d %b %Y")
df = df[COLS.keys()]
df.sort_values(by='bed_code', inplace=True)


columns=[{"name": i, "id": i} for i in df.columns if i in COLS.keys()]
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
    style_cell={'padding': '5px'},
    style_cell_conditional=[
        {
            'if': {'column_id': 'name'},
            'textAlign': 'left'
        }
    ],
    sort_action='native',
    page_size=10,
    style_table={'overflowX': 'auto'},
    )])

if __name__ == "__main__":
    app.run_server(debug=True)
