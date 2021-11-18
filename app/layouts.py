"""
Layouts organised for sitrep
- header
- main
- footer
- dash_only (to store non visible parts of the app)
"""

from dash import Dash, Input, Output, State, html, dcc
from dash import dash_table as dt
import dash_bootstrap_components as dbc

from config import ConfigFactory
conf = ConfigFactory.factory()

# a bright banner across the top of the page
header = html.Div(
    dbc.Row([
        dbc.Col(html.H1("Sitrep v2", className="bg-primary text-white p-2"), md=12),
    ])
)

# main page body currently split into two columns 9:3
main = html.Div([
    # Full width row
    dbc.Row([
            html.Div([html.H3('UCLH T03 ICU Current Patients')]),
            ]),

    dbc.Row([
        # Heading of LEFT 3/12 COLUMN
        dbc.Col([
            html.Div(id="datatable-side"),
        ], md=3),

        # Heading of RIGHT 9/12 COLUMN
        dbc.Col([

            dbc.Card([
                dbc.CardHeader("Ward level metrics"),
                dbc.CardBody([
                    html.H3("Work Intensity"),
                    html.Div( id="wim-graduated-bar" ),
                    html.P("This is an estimate based on the overall burden of organ support")
                ])
            ]),

            dbc.Card([
                dbc.CardHeader(
                    "Patient details after selcting from the side table"),
                dbc.CardBody([
                    html.Div(id="datatable-patient")
                ])
            ]),

            dbc.Card([
                dbc.CardHeader("Patients displayed by bed number"),
                dbc.CardBody([

                    # html.Div([ html.P('Patients displayed by bed number', className="card-text"), ]),

                    html.Div(dcc.Graph(
                        id='polar-main',
                        config={
                            'responsive': True,
                            'autosizable': True,
                            'displaylogo': False,
                        }
                    )),
                ])
            ]),




        ], md=9),
    ], align='start')
])

# footer! mainly marking the end of the page
# but perhaps put the patient detail here
footer = html.Div(
    dbc.Row([
        dbc.Col(
            html.Div([
                dbc.Alert(id='msg'),
                # html.P(id='msg'),
                html.P("Here is some detailed note held in the footer")
            ]), md=12),
    ])
)


# use this to store dash components that you don't need to 'see'
dash_only = html.Div([
    dcc.Interval(id="interval-data",
                 interval=conf.REFRESH_INTERVAL, n_intervals=0),
    # use this to signal when the data changes
    dcc.Store(id="signal"),
    # dcc.Store(id="tbl-active-row"),
    dcc.Store(id="tbl-side-selection"),
])

# """Principal layout for sitrep2 page"""
sitrep = dbc.Container(
    fluid=True,
    children=[
        header,
        main,
        footer,
        dash_only,
    ]
)
