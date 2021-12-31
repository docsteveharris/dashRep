import arrow
import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import wrangle as wng
from config import ConfigFactory, footer, header, nav
from dash import Dash, Input, Output, State
from dash import dash_table as dt
from dash import dcc, html

conf = ConfigFactory.factory()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
)

discharge_options = ["Ready", "Review", "No"]

# Simulate an offline store of data by making a CSV file
# prepare the data as a list of dictionaries (i.e. pd.DataFrame.from_records(data))
df_orig = pd.DataFrame.from_records([
    {"original-data": i, "input-data": i, "discharge-data": "No"} for i in range(11)
])
df_orig.to_csv("scratch.csv", index=False)



app.layout = html.Div(
    [
        html.Div(id="msg-data-saved"),
        html.Div(id="computed-table-container"),
        html.Button(id="reset-data", n_clicks=0, children="Reset data"),
        html.Button(id="submit-data", n_clicks=0, children="Submit data"),
        dcc.Interval(id="interval-data", interval=conf.REFRESH_INTERVAL, n_intervals=0),
        dcc.Store(id="table-data"),
    ]
)


@app.callback(
    Output("table-data", "data"),
    Input("interval-data", "n_intervals"),
    Input("reset-data", "n_clicks"),
)
def load_data(n_intervals, n_clicks):
    # read the data in from an external store
    df = pd.read_csv("scratch.csv")
    df = df.to_dict("records")
    return df


@app.callback(
    Output("msg-data-saved", "children"),
    Input("submit-data", "n_clicks"),
    State("computed-table", "data"),
    prevent_initial_call=True,  # suppress_callback_exceptions does not work
    )
def write_data(n_clicks, data):
    print(">>> saving data")
    df = pd.DataFrame.from_records(data)
    df.to_csv("scratch.csv", index=False)
    now = arrow.now()
    return f"Data saved at {now}"



@app.callback(
    Output("computed-table-container", "children"),
    Input("table-data", "data"),
    Input("reset-data", "n_clicks"),
)
def draw_table(data, n_clicks):
    # The first time only; edits to the table do not call this function again
    print('>>> running draw_table()')
    data = data
    return [
        dt.DataTable(
            id="computed-table",
            columns=[
                {"name": "Original Data", "id": "original-data"},
                {"name": "Input Data", "id": "input-data", "editable": True},
                {"name": "Input Squared", "id": "output-data"},
                {
                    "name": "Discharge",
                    "id": "discharge-data",
                    "editable": True,
                    "presentation": "dropdown",
                },
            ],
            # this input value is only used the first time the data is loaded
            data=data,
            dropdown={
                "discharge-data": {
                    "options": [{"label": i, "value": i} for i in discharge_options]
                }
            },
            editable=False,
            cell_selectable=True,
        ),
    ]

@app.callback(
    Output("computed-table", "data"),
    Input("computed-table", "data_timestamp"),
    State("computed-table", "data"),
)
def update_columns(timestamp, rows):
    for row in rows:
        try:
            row["output-data"] = float(row["input-data"]) ** 2
        except:
            row["output-data"] = "NA"
    print(pd.DataFrame.from_records(rows))
    return rows




if __name__ == "__main__":
    app.run_server(
        port=8010,
        host="0.0.0.0",
        debug=True,
    )

