"""
Functions (callbacks) that provide the functionality
"""
import json
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


@app.callback(
    Output("datatable-side", "children"),
    [
        Input("signal", "data"),
        Input("polar-main", "clickData"),
    ]
)
def gen_datatable_side(json_data, polar_click):
    COL_NAMES = [{"name": v, "id": k}
                 for k, v in conf.COLS.items() if k in conf.COLS_SIDEBAR]

    if polar_click:
        pSelectIndex = [polar_click['points'][0]['pointIndex']]
    else:
        pSelectIndex = []
    print(pSelectIndex)

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
            # style_table={"overflowX": "auto"},
            # filter_action="native",
            sort_action="native",
            cell_selectable=False,
            row_selectable='single',
            selected_row_ids=[],
            selected_rows=pSelectIndex,
            # TODO: does not work with paginated tables
            # page_size=10,
        ),
    ]


@app.callback(
    Output("polar-main", "figure"),
    [
        Input("signal", "data"),
        Input("polar-main", "clickData"),
    ]
)
def draw_fig_polar(data, selection):
    """
    Draws a fig polar.

    :param      'data':  The data
    :type       'data':  { type_description }
    """

    df = pd.DataFrame.from_records(data)

    fig = go.Figure()
    fig.add_trace(
        # go.Barpolar(
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

    # fig.update_traces(textposition='top left')
    fig.update_traces(marker_line_color='rgba(0,0,0,1)')
    fig.update_traces(marker_opacity=0.8)
    fig.update_traces(marker_size=20)
    # fig.update_traces(name='Predicted ward LoS')

    # update polar plot
    fig.update_polars(bgcolor='#FFF')
    fig.update_polars(hole=0.6)
    # fig.update_polars(sector=[0, 350])

    fig.update_polars(angularaxis_showgrid=True)
    fig.update_polars(angularaxis_gridcolor='#EEE')
    fig.update_polars(angularaxis_linecolor='grey')  # outer ring
    fig.update_polars(angularaxis_ticks='outside')
    fig.update_polars(angularaxis_direction='counterclockwise')

    fig.update_polars(radialaxis_showgrid=True)
    fig.update_polars(radialaxis_color='#999')
    fig.update_polars(radialaxis_gridcolor='#EEE')

    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))

    # update traces
    # fig.update_traces(opacity=0.5)
    fig.update_traces(hovertemplate="LoS: %{r} Bed: %{theta}")

    if selection:
        pSelectIndex = [selection['points'][0]['pointIndex']]
        print(pSelectIndex)
        fig.update_traces(selectedpoints=pSelectIndex,
                          selector=dict(type='scatterpolar'))
        fig.update_traces(selected_marker_size=50,
                          selector=dict(type='scatterpolar'))
        # fig.update_traces(selected_marker_opacity=1.0)

    return fig


@app.callback(
    Output('msg', 'children'),
    [
        Input('tbl-active-row', 'data'),
        Input('polar-main', 'clickData'),
    ]
)
def gen_msg(active_row, polar_click):
    row_id = 'NOT IMPLEMENTED'
    row = (str(active_row)
           if active_row else "MISSING")
    row_text = (f"Row is {row} and Row ID is {row_id}"
                if row or row_id else "Click the table")
    if not polar_click:
        polar_txt = "No point clicked"
    else:
        pDict = polar_click['points'][0]
        pIndex = pDict['pointIndex']
        pText = pDict['text']
        polar_txt = f"You clicked point {pIndex} with the label {pText}"

    return f"""{row_text} AND {polar_txt}"""


@app.callback(
    Output('tbl-active-row', 'data'),
    Input('tbl-side', 'derived_virtual_selected_rows'))
def get_datatable_side_selected_row(row_id):
    """returns the row id selected from the datatable (side bar)"""
    print(row_id)
    if row_id:
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
