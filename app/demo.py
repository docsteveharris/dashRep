import os
import json
from dotenv import load_dotenv
from collections import OrderedDict
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

import plotly.graph_objects as go

import dash
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

import data_mx as dmx

dotenv_path = Path(".env")  # runs from project root
load_dotenv(dotenv_path=dotenv_path)

if os.getenv("DEVELOPMENT") == 'True':
    DEV_HYLODE = True
    HYLODE_DATA_SOURCE = Path("data/icu.json")
    DEV_USER = True
    USER_DATA_SOURCE = Path("data/user_edits.csv")
else:
    # Use the IP address b/c slow on DNS resolution
    # HYLODE_DATA_SOURCE = 'http://uclvlddpragae08:5006/icu/live/T06/ui'
    DEV_HYLODE = False
    HYLODE_DATA_SOURCE = "http://172.16.149.205:5006/icu/live/T03/ui"
    DEV_USER = True
    USER_DATA_SOURCE = Path("data/user_edits.csv")

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8009

# Checks for remote updates on the server
# TODO: feels like we need to run as a check that looks for an update time stamp but does not update the table
# until the server data changes
REFRESH_INTERVAL = 5 * 60 * 1000  # milliseconds

COLS = OrderedDict(
    {
        "ward_code": "Ward",
        # 'bed_code': 'Bed code',
        "bay": "Bay",
        "bed": "Bed",
        # 'admission_dt': 'Admission',
        "elapsed_los_td": "LoS",
        "mrn": "MRN",
        "name": "Full Name",
        "admission_age_years": "Age",
        "sex": "Sex",
        # "dob": "DoB",
        "wim_1": "WIM-P",
        "wim_r": "WIM-R",
    }
)
COL_NAMES = [{"name": v, "id": k} for k, v in COLS.items()]


app = dash.Dash(
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME,
    ]  # or BOOTSTRAP or SOLAR
)
app.config.suppress_callback_exceptions = True


def layout_text_card():
    """Title and text at the top of the page"""
    return dbc.Card(
                dbc.CardBody(
                    [
                        html.H2("SitRep Dashboard", className="card-title"),
                        html.H4("v2 (Dash)", className="card-subtitle"),
                        html.Div(
                            [
                                html.P(
                                    """Plot below is for T3 beds; radius is the 'work intensity', and colour is the elapased LoS!""",
                                    className="card-text",
                                )
                            ]
                        ),
                    ]
                )
            , color='secondary',
            # style={'width': '888rem'}
            className="w-50"
        )


def layout_new_value():
    """Data entry box for editing values selected from the table"""
    return html.Div(
        dbc.Card(
            dbc.CardBody(
                    html.Div(
                        [
                            dbc.Label('Click a WIM cell to update'),
                            dbc.Input(id="new-value", type="number", min=0, max=10),
                            # dbc.FormText('Type into the box above'),
                            dbc.Button( id="submit-button", n_clicks=0, children="Submit"),
                        ]
                    ),
            ),
        color='info')
    )


def layout_fig_polar():
    """Polar plot showing ward layout"""
    return html.Div(
        dcc.Graph(
            id="fig-polar",
            # style={'width': '500px'},
            config={
                "responsive": True,
                "autosizable": True,
            },
        ),
        # md=6
    )


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.CardGroup([
                    layout_text_card(),
                    layout_new_value(),
                ])
            ]
        ),
        dbc.Alert(id="active-cell-value"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(layout_fig_polar()),
                dbc.Col(html.Div(id="datatable"), width=7)]
        ),
        html.Br(),
        # dbc.Alert(layout_new_value(), color="info"),
        dcc.Interval(id="interval-data", interval=REFRESH_INTERVAL, n_intervals=0),
        # use this to signal when the data changes
        dcc.Store(id="signal"),
        dcc.Store(id="tbl-active-cell"),
    ],
    fluid=True
)


@app.callback(Output("datatable", "children"), [Input("signal", "data")])
def gen_datatable(json_data):
    global COL_NAMES
    return [
        dt.DataTable(
            id="tbl",
            columns=COL_NAMES,
            data=json_data,
            editable=False,
            style_cell={
                "fontSize": 14,
                # 'font-family':'sans-serif',
                "padding": "3px",
            },
            style_cell_conditional=[{"if": {"column_id": "name"}, "textAlign": "left"}],
            style_table={"overflowX": "auto"},
            filter_action="native",
            sort_action="native",
            # TODO: does not work with paginated tables
            # page_size=10,
        ),
    ]


@app.callback(Output("fig-polar", "figure"), Input("signal", "data"))
def draw_fig_polar(data):
    """
    Draws a fig polar.

    :param      'data':  The data
    :type       'data':  { type_description }
    """
    df = pd.DataFrame.from_records(data)

    fig = go.Figure()
    fig.add_trace(
        go.Barpolar(
            theta=df["bed"],
            marker_color=np.log(df["elapsed_los_td"] + 1),
            r=df[["wim_1", "wim_r"]].max(axis=1),
            # mode='markers',
            hovertemplate="WIM: %{r} Bed: %{theta}",
        )
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    fig.update_layout(autosize=True)
    # fig.update_traces(hovertemplate="LoS: %{r} Bed: %{theta}")
    return fig


@app.callback(
    Output("new-value", "value"), Input("tbl", "active_cell"), State("tbl", "data")
)
def update_input_default(cell, data):
    """Updates the default value for the user input"""
    if cell:
        col = cell["column_id"]
        row = cell["row"]
        val = data[row][col]  # uses data to get value
    else:
        val = None
    return val


@app.callback(
    Output("tbl-active-cell", "data"),
    Input("tbl", "active_cell"),
)
def update_active_cell_store(cell):
    """Stores the active cell dictionary so available to other components"""
    # TODO: active cell refers to the displayed data; need to know the row of the underlying source
    # else you get the wrong reference when data is paginated or filtered
    # prob need to provide a row_id key
    if cell:
        return cell


@app.callback(
    Output("active-cell-value", "children"),
    Input("tbl-active-cell", "data"),
    State("tbl", "data"),
)
def active_cell_status(cell, data) -> str:
    """Banner reporting which cell was selected"""
    if not cell:
        return "No cell selected!"

    col = cell["column_id"]
    row = cell["row"]
    val = data[row][col]  # uses data to get value

    msg = (
        f"Cell ({cell['row']},{cell['column']}) with the value {val} has been selected"
    )

    return msg


@app.callback(
    Output("interval-data", "n_intervals"),  # reset the interval timer?
    [Input("submit-button", "n_clicks")],
    [
        State("new-value", "value"),
        State("signal", "data"),
        State("tbl-active-cell", "data"),
    ],
)
def update_value(n_clicks, new_value, data, cell):
    """
    writes the data back to the original data source
    this in turn then triggers the data table to reload
    """
    global HYLODE_DATA_SOURCE

    if cell:
        col = cell["column_id"]
        row = cell["row"]
        val = data[row][col]  # uses data to get value

    if n_clicks > 0:
        df = pd.DataFrame.from_records(data)

        df.loc[row, "wim_r"] = new_value
        df_filtered_by_row = df.loc[row]
        dmx.write_data(df_filtered_by_row, USER_DATA_SOURCE)
    return 0


# TODO n_intervals arg is unused but just ensures that store data updates
@app.callback(Output("signal", "data"), Input("interval-data", "n_intervals"))
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
    return df.to_dict("records")


if __name__ == "__main__":
    app.run_server(port=SERVER_PORT, host=SERVER_HOST, debug=True)
