"""
Functions (callbacks) that provide the functionality
"""
import json
import numpy as np
import pandas as pd

import plotly.graph_objects as go

import dash_daq as daq
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State
from dash import dash_table as dt
from dash import dcc, html

import wrangle as wng
from config import ConfigFactory
from app import app

conf = ConfigFactory.factory()


@app.callback(
    Output("datatable-patient", "children"),
    [
        Input("tbl-side-selection", "data"),
        Input("signal", "data"),
    ],
)
def gen_datatable_patient(row_id, json_data):
    """
    Draw the patient level data

    :param      row_id:  the row selected from the side datatable
    :param      data:        the patient data
    """
    # filter cols
    COL_NAMES = [
        {"name": v, "id": k} for k, v in conf.COLS.items() if k in conf.COLS_FULL
    ]

    # TODO: shouldn't need to do a roundtrip through a pandas dataframe
    # filter the json data by the selected table row
    df = pd.DataFrame.from_records(json_data)
    df = df[df["id"] == row_id]  # must use tbl id
    json_data = df.to_dict("records")

    return [
        dt.DataTable(
            id="tbl-patient", columns=COL_NAMES, data=json_data, editable=False
        )
    ]


@app.callback(
    Output("datatable-side", "children"),
    [
        Input("signal", "data"),
    ],
)
def gen_datatable_side(json_data):
    COL_NAMES = [
        {"name": v, "id": k} for k, v in conf.COLS.items() if k in conf.COLS_SIDEBAR
    ]

    return [
        dt.DataTable(
            id="tbl-side",
            columns=COL_NAMES,
            data=json_data,
            editable=False,
            # active_cell=True,
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
            style_data={"color": "black", "backgroundColor": "white"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgb(220, 220, 220)"}
            ],
            sort_action="native",
            cell_selectable=True,  # possible to click and navigate cells
            row_selectable="single",
        ),
    ]


@app.callback(
    Output("polar-main", "figure"),
    [
        Input("tbl-side-selection", "data"),
        Input("compass-picker", "value"),
        Input("signal", "data"),
    ],
)
def draw_fig_polar(row_id, team, data):
    """
    Draws a fig polar.

    :param      'team':  result from switches picking which parts of the data to show
    :type       'data':  { type_description }

    :param      'data':  The data
    :type       'data':  { type_description }
    """

    df = pd.DataFrame.from_records(data)
    fig = go.Figure()

    if not team:
        # return emppty space if no team selected
        return fig
    else:
        df = df[df.team.isin(team)]

    # Prep discharge status
    df['discharge_indicator'] = 0.0
    df.loc[df.discharge_ready_1_4h == 'No', 'discharge_indicator'] = 0.0
    df.loc[df.discharge_ready_1_4h == 'Yes', 'discharge_indicator'] = 1.0
    df.loc[df.discharge_ready_1_4h == 'Review', 'discharge_indicator'] = 0.5

    # set up markers for empty beds
    df.loc[df.bed_empty, "elapsed_los_td"] = 1  # 1 seconds
    df.loc[df.bed_empty, "wim_r"] = 0  # zero work intensity

    fig.add_trace(
        go.Scatterpolar(

            mode="markers+text",
            name="",  # names the 'trace'

            # ward bed
            theta=df["bed"],

            # marker radial position indicates discharge status
            # edge = escape ; centre = plughole / not ready
            r=df['discharge_indicator'],
            marker_line_color=df["discharge_indicator"],
            marker_line_width=2 + df["discharge_indicator"] * 4,

            # inner color indicates severity of illness/work
            marker_color="#FFF",
            # marker_color=df[["wim_1", "wim_r"]].max(axis=1),
            marker_size=20 + df[["wim_1", "wim_r"]].max(axis=1) * 5,

            # text indicates WIM
            text=df[["wim_1", "wim_r"]].max(axis=1),

            hovertemplate="WIM: %{r} Bed: %{theta}",
        )
    )

    # update layout
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))

    # update polar plot
    fig.update_polars(bgcolor="#FFF")

    # scale the 'hole' so that markers don't overlap when at baseline
    fig.update_polars(hole=0.70)  # fraction of radius to remove

    fig.update_polars(angularaxis_layer="below traces") #  so markers are above grid lines
    fig.update_polars(angularaxis_showgrid=True)
    fig.update_polars(angularaxis_showline=False)
    fig.update_polars(angularaxis_gridcolor="#EBEBEB")
    # tick combination below leaves nice space around angular lines
    fig.update_polars(angularaxis_ticks="outside")  # "" not ticks or "outside" or "inside"
    fig.update_polars(angularaxis_tickcolor="#FFF") # tick color match backgrund
    fig.update_polars(angularaxis_direction="clockwise")

    fig.update_polars(radialaxis_layer="below traces") #  so markers are above grid lines
    fig.update_polars(radialaxis_showgrid=False)  # removes grid
    fig.update_polars(radialaxis_showline=False)
    fig.update_polars(radialaxis_ticks="")  # do not draw the tickss
    fig.update_polars(radialaxis_showticklabels=False)  # removes axis labels


    # set up colors for identifying d/c
    # https://plotly.com/python/reference/scatterpolar/#scatterpolar-marker-colorscale

    fig.update_traces(marker_symbol="circle")
    # color the marker centre
    fig.update_traces(marker_colorscale=[
        [0, 'rgb(255, 118, 0 )'],
        [1, 'rgb(255, 0, 0 )'],
        ])
    # fig.update_traces(marker_gradient_type="radial")
    # fig.update_traces(marker_gradient_color="#F00")

    # color the marker line (discharge)
    fig.update_traces(marker_line_colorscale=[
        [0.0, 'rgb(255,69,58)'],
        [0.5, 'rgb(255, 118, 0)'],
        [1.0, 'rgb(15,136,0)'],
        ])


    # fig.update_traces(marker_sizemin=30)
    # fig.update_traces(marker_size=25)

    fig.update_traces(hovertemplate="LoS: %{r} Bed: %{theta}")

    dfi = df.reset_index(drop=True)

    if row_id and row_id in list(dfi.bed_code):
        row_num = dfi[dfi["id"] == row_id].index[0]
        row_nums = []
        row_nums.append(row_num)
        fig.update_traces(selectedpoints=row_nums, selector=dict(type="scatterpolar"))
        # fig.update_traces(selected_marker_size=40, selector=dict(type="scatterpolar"))
        fig.update_traces(selected_marker_opacity=1, selector=dict(type="scatterpolar"))
        fig.update_traces(unselected_marker_opacity=0.5, selector=dict(type="scatterpolar"))
        # fig.update_traces(
        #     selected_marker_color="grey", selector=dict(type="scatterpolar")
        # )
        fig.update_traces(
            selected_textfont_color="black", selector=dict(type="scatterpolar")
        )

    return fig


@app.callback(Output("occ-graduated-bar", "children"), Input("signal", "data"))
def gen_graduated_bar_occ(json_data, occ_max=35):
    """
    Generates the graduated bar summarising current occupancy

    :param      json_data:  json representation of the current dataframe
    :type       json_data:  { type_description }
    """
    df = pd.DataFrame.from_records(json_data)

    occ = df.mrn.count()
    occ_scaled = occ / occ_max * 10

    res = daq.GraduatedBar(
        color={
            "gradient": True,
            "ranges": {"green": [0, 4], "yellow": [4, 7], "red": [7, 10]},
        },
        showCurrentValue=True,
        # vertical=True,
        value=occ_scaled,
    )

    return res


@app.callback(Output("wim-graduated-bar", "children"), Input("signal", "data"))
def gen_graduated_bar_wim(json_data, wim_max=175):
    """
    Generates the graduated bar summarising current work intensity
    Assumes the max possible is ?5x the number number of beds

    :param      json_data:  json representation of the current dataframe
    :type       json_data:  { type_description }
    """
    df = pd.DataFrame.from_records(json_data)

    wim_sum = df[["wim_1", "wim_r"]].max(axis=1).sum()
    wim_sum_scaled = wim_sum / wim_max * 10

    res = daq.GraduatedBar(
        color={
            "gradient": True,
            "ranges": {"green": [0, 4], "yellow": [4, 7], "red": [7, 10]},
        },
        showCurrentValue=True,
        # vertical=True,
        value=wim_sum_scaled,
    )

    return res


@app.callback(
    Output("msg", "children"),
    [
        Input("tbl-side-selection", "data"),
    ],
)
def gen_msg(active_row):
    if not active_row:
        res = """Click the table"""

    res = str(active_row)
    res = f"Selected row id is {res}"
    return res


@app.callback(
    Output("tbl-side-selection", "data"),
    Input("tbl-side", "derived_virtual_selected_row_ids"),
    State("signal", "data"),
)
def get_datatable_side_selected_row(row_id, json_data):
    """
    returns the 'row_id' selected from the datatable (side bar)
    if nothing selected then returns the first row
    """
    if not row_id:
        row_id = json_data[0]["id"]
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
    df_hylode = wng.get_hylode_data(conf.HYLODE_DATA_SOURCE, dev=conf.DEV_HYLODE)
    ward = df_hylode["ward_code"][0]
    df_user = wng.get_user_data(conf.USER_DATA_SOURCE, dev=conf.DEV_USER)
    df_skeleton = wng.get_bed_skeleton(ward, conf.SKELETON_DATA_SOURCE, dev=conf.DEV)
    df_orig = wng.merge_hylode_user_data(df_skeleton, df_hylode, df_user)
    df = wng.wrangle_data(df_orig, conf.COLS)
    return df.to_dict("records")



"""
Layouts organised for sitrep
- header
- main
- footer
- dash_only (to store non visible parts of the app)
"""

# a bright banner across the top of the page

BANNER_TXT = ("Sitrep v2: UCLH T03 current ICU patients",)
header = html.Div(
    dbc.Row(
        [
            dbc.Col(html.H1(BANNER_TXT, className="bg-primary text-white p-2"), md=12),
        ]
    )
)

# main page body currently split into two columns 9:3
main = html.Div(
    [
        # # Full width row
        # dbc.Row([
        #         html.Div([html.H2('UCLH T03 ICU Current Patients')]),
        #         ]),
        dbc.Row(
            [
                # Heading of LEFT 3/12 COLUMN
                dbc.Col(
                    [
                        html.Div(id="datatable-side"),
                    ],
                    md=3,
                ),
                # Heading of RIGHT 9/12 COLUMN
                dbc.Col(
                    [
                        dbc.Row([
                                dbc.Col([html.Div(
                                    dbc.Checklist(
                                        id='compass-picker',
                                        options=[
                                        {'label': ' North ', 'value': 'North'},
                                        {'label': ' South ', 'value': 'South'},
                                        {'label': ' PACU ', 'value': 'PACU'},
                                        ],
                                        value=['North', 'South'],
                                        switch=True,
                                        inline=True,
                                        ))],
                                    md=6),
                                dbc.Col(html.H2(
                                    "Ward level metrics", style={"textAlign": "right"} ), md=6),
                            ]),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Ward occupancy"),
                                                dbc.CardBody(
                                                    [
                                                        html.Div(
                                                            id="occ-graduated-bar"
                                                        ),
                                                        html.P(
                                                            "Based on the total possible beds (not staff)"
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Work Intensity"),
                                                dbc.CardBody(
                                                    [
                                                        html.Div(
                                                            id="wim-graduated-bar"
                                                        ),
                                                        html.P(
                                                            "Based on the overall burden of organ support"
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    md=6,
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Patient details after selcting from the side table"
                                                ),
                                                dbc.CardBody(
                                                    [html.Div(id="datatable-patient")]
                                                ),
                                            ]
                                        ),
                                    ],
                                    md=12,
                                )
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Patients displayed by bed number"
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        # html.Div([ html.P('Patients displayed by bed number', className="card-text"), ]),
                                                        html.Div(
                                                            dcc.Graph(
                                                                id="polar-main",
                                                                config={
                                                                    "responsive": True,
                                                                    "autosizable": True,
                                                                    "displaylogo": False,
                                                                },
                                                            )
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    md=12,
                                )
                            ]
                        ),
                    ],
                    md=9,
                ),
            ],
            align="start",
        )
    ]
)

# footer! mainly marking the end of the page
# but perhaps put the patient detail here
footer = html.Div(
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        dbc.Alert(id="msg"),
                        # html.P(id='msg'),
                        html.P("Here is some detailed note held in the footer"),
                    ]
                ),
                md=12,
            ),
        ]
    )
)


# use this to store dash components that you don't need to 'see'
dash_only = html.Div(
    [
        dcc.Interval(id="interval-data", interval=conf.REFRESH_INTERVAL, n_intervals=0),
        # use this to signal when the data changes
        dcc.Store(id="signal"),
        # dcc.Store(id="tbl-active-row"),
        dcc.Store(id="tbl-side-selection"),
    ]
)

# """Principal layout for sitrep2 page"""
sitrep = dbc.Container(
    fluid=True,
    children=[
        header,
        main,
        footer,
        dash_only,
    ],
)
