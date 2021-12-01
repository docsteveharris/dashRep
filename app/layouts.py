"""
Layouts organised for sitrep
- header
- main
- footer
- dash_only (to store non visible parts of the app)
"""

import dash_bootstrap_components as dbc
from config import ConfigFactory
from dash import Dash, Input, Output, State
from dash import dash_table as dt
from dash import dcc, html

conf = ConfigFactory.factory()

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
                        dbc.Row(
                            [
                                html.H2(
                                    "Ward level metrics", style={"textAlign": "right"}
                                ),
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
                                                            "This is an estimate based on the overall burden of organ support"
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

# For debugging
import wrangle as wng
df_hylode = wng.get_hylode_data(conf.HYLODE_DATA_SOURCE, dev=conf.DEV_HYLODE)
print(df_hylode.head())
debug = html.Div([
    dt.DataTable(
        id='debug',
        columns = [{"name": i, "id": i} for i in df_hylode.columns],
        data=df_hylode.to_dict('records'),
        filter_action="native",
        sort_action="native"

        )
])

