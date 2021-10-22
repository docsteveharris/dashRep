from pathlib import Path

import pandas as pd

import dash
from dash import Dash, Input, Output, callback
from dash import dash_table as dt
import dash_bootstrap_components as dbc

DATA_SOURCE = Path('../data/icu.json')
# TODO convert to ordered dictionary
COLS = {
    'mrn': 'MRN',
    'name': 'Full Name',
    'sex': 'Sex',
    'dob': 'DoB',
    'admission_age_years': 'Age',
    'ward_code': 'Ward',
    'bed_code': 'Bed',
    'wim_1': 'Work Intensity'}



df = pd.read_json(DATA_SOURCE)

# Prep and wrangle

df['admission_dt'] = pd.to_datetime(df['admission_dt'], infer_datetime_format=True)
df['admission_dt'] = df['admission_dt'].dt.strftime("%H:%M %d %b %Y")


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
    page_size=5,
    style_table={'overflowX': 'auto'},
    )])

if __name__ == "__main__":
    app.run_server(debug=True)
