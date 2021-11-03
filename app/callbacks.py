from app import app
from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
# import dash_bootstrap_components as dbc

import plotly.graph_objects as go

import pandas as pd
import numpy as np

from config import ConfigFactory
conf = ConfigFactory.factory()
import wrangle as wng

@app.callback(Output("datatable", "children"), [Input("signal", "data")])
def gen_datatable(json_data):
    COL_NAMES = [{"name": v, "id": k} for k, v in conf.COLS.items() if k in conf.COLS_SIDEBAR]
    return [
        dt.DataTable(
            id="tbl",
            columns=COL_NAMES,
            data=json_data,
            editable=False,
            style_cell={
                "fontSize": 12,
                # 'font-family':'sans-serif',
                "padding": "2px",
            },
            style_cell_conditional=[{"if": {"column_id": "name"}, "textAlign": "left"}],
            style_table={"overflowX": "auto"},
            # filter_action="native",
            sort_action="native",
            # TODO: does not work with paginated tables
            # page_size=10,
        ),
    ]


# @app.callback(Output("fig-polar", "figure"), Input("signal", "data"))
# def draw_fig_polar(data):
#     """
#     Draws a fig polar.

#     :param      'data':  The data
#     :type       'data':  { type_description }
#     """
#     df = pd.DataFrame.from_records(data)

#     fig = go.Figure()
#     fig.add_trace(
#         go.Barpolar(
#             theta=df["bed"],
#             marker_color=np.log(df["elapsed_los_td"] + 1),
#             r=df[["wim_1", "wim_r"]].max(axis=1),
#             # mode='markers',
#             hovertemplate="WIM: %{r} Bed: %{theta}",
#         )
#     )
#     fig.update_layout(showlegend=False)
#     fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
#     fig.update_layout(autosize=True)
#     # fig.update_traces(hovertemplate="LoS: %{r} Bed: %{theta}")
#     return fig


# @app.callback(
#     Output("new-value", "value"), Input("tbl", "active_cell"), State("tbl", "data")
# )
# def update_input_default(cell, data):
#     """Updates the default value for the user input"""
#     if cell:
#         col = cell["column_id"]
#         row = cell["row"]
#         val = data[row][col]  # uses data to get value
#     else:
#         val = None
#     return val


# @app.callback(
#     Output("tbl-active-cell", "data"),
#     Input("tbl", "active_cell"),
# )
# def update_active_cell_store(cell):
#     """Stores the active cell dictionary so available to other components"""
#     # TODO: active cell refers to the displayed data; need to know the row of the underlying source
#     # else you get the wrong reference when data is paginated or filtered
#     # prob need to provide a row_id key
#     if cell:
#         return cell


# @app.callback(
#     Output("active-cell-value", "children"),
#     Input("tbl-active-cell", "data"),
#     State("tbl", "data"),
# )
# def active_cell_status(cell, data) -> str:
#     """Banner reporting which cell was selected"""
#     if not cell:
#         return "No cell selected!"

#     col = cell["column_id"]
#     row = cell["row"]
#     val = data[row][col]  # uses data to get value

#     msg = (
#         f"Cell ({cell['row']},{cell['column']}) with the value {val} has been selected"
#     )

#     return msg


# @app.callback(
#     Output("interval-data", "n_intervals"),  # reset the interval timer?
#     [Input("submit-button", "n_clicks")],
#     [
#         State("new-value", "value"),
#         State("signal", "data"),
#         State("tbl-active-cell", "data"),
#     ],
# )
# def update_value(n_clicks, new_value, data, cell):
#     """
#     writes the data back to the original data source
#     this in turn then triggers the data table to reload
#     """

#     if cell:
#         col = cell["column_id"]
#         row = cell["row"]
#         val = data[row][col]  # uses data to get value

#     if n_clicks > 0:
#         df = pd.DataFrame.from_records(data)

#         df.loc[row, "wim_r"] = new_value
#         df_filtered_by_row = df.loc[row]
#         wng.write_data(df_filtered_by_row, conf.USER_DATA_SOURCE)
#     return 0


# TODO n_intervals arg is unused but just ensures that store data updates
@app.callback(Output("signal", "data"), Input("interval-data", "n_intervals"))
def update_data_from_source(n_intervals):
    """
    stores the data in a dcc.Store
    runs on load and will be triggered each time the table is updated or the REFRESH_INTERVAL elapses
    """
    df_hylode = wng.get_hylode_data(conf.HYLODE_DATA_SOURCE, dev=conf.DEV_HYLODE)
    df_user = wng.get_user_data(conf.USER_DATA_SOURCE, dev=conf.DEV_USER)
    df_orig = wng.merge_hylode_user_data(df_hylode, df_user)
    df = wng.wrangle_data(df_orig, conf.COLS)
    return df.to_dict("records")
