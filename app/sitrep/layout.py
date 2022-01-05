import dash_bootstrap_components as dbc
from dash import dcc, html
from . import callbacks


from config.config import ConfigFactory, footer, header, nav
conf = ConfigFactory.factory()


"""
Layouts organised for sitrep
- header (from config)
- nav (from config)
- main
- footer (from config)
- dash_only (to store non visible parts of the app)
"""

icu_radio_button = html.Div(
    [
        html.Div(
            [
                dbc.RadioItems(
                    id="icu_radio",
                    className="dbc d-grid d-md-flex justify-content-md-end btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active btn-primary",
                    options=[
                        {"label": "T03", "value": "T03"},
                        {"label": "T06", "value": "T06"},
                        {"label": "GWB", "value": "GWB"},
                        {"label": "WMS", "value": "WMS"},
                        {"label": "NHNN", "value": "NHNN"},
                    ],
                    value="T03",
                )
            ],
            className="dbc",
        ),
        # html.Div(id="which_icu"),
    ],
    className="radio-group",
)

save_reset_button = html.Div(
    [
        # dbc.ButtonGroup(
        # [
        dbc.Button(
            "Save", id="tbl-save", color="success", n_clicks=0, outline=False, size="md"
        ),
        dbc.Button(
            "Reset",
            id="tbl-reset",
            color="warning",
            n_clicks=0,
            outline=False,
            size="md",
        ),
        # ]
        # ),
    ],
)

# main page body currently split into two columns 9:3
main = dbc.Container(
    [
        # All unit content here plus unit selector
        dbc.Row(
            [
                dbc.Col([icu_radio_button], width={"offset": 6, "width": 4}),
                # dbc.Col( [ html.Div(id="which_icu"),], md=6 ),
                dbc.Col([save_reset_button], md=2),
            ],
            # className="g-0",
            justify="between",
        ),
        # Unit specific content here
        dbc.Row(
            [
                dbc.Col(
                    [html.Div(id="datatable-main")],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Ward aggregate details"),
                                        dbc.CardBody("CardBody"),
                                        dbc.CardFooter("CardFooter"),
                                    ]
                                ),
                            ],
                            align="start",
                        ),
                        dbc.Row(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Patient specific details"),
                                        dbc.CardBody("CardBody"),
                                        dbc.CardFooter("CardFooter"),
                                    ]
                                ),
                            ],
                            align="end",
                        ),
                    ],
                    md=6,
                ),
            ],
            align="start",
        ),
    ],
    fluid=True,
    # className="dbc",
)


# use this to store dash components that you don't need to 'see'
dash_only = html.Div(
    [
        dcc.Interval(id="interval-data", interval=conf.REFRESH_INTERVAL, n_intervals=0),
        # which ICU?
        dcc.Store(id="icu_active"),
        # use this to source-data when the data changes
        dcc.Store(id="source-data"),
        # dcc.Store(id="tbl-active-row"),
        dcc.Store(id="tbl-side-selection"),
    ]
)

# """Principal layout for sitrep2 page"""
sitrep = dbc.Container(
    fluid=True,
    className="dbc",
    children=[
        header,
        nav,
        main,
        footer,
        dash_only,
    ],
)
