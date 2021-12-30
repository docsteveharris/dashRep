"""
Load configurations using a base config class design pattern
as per https://stackoverflow.com/a/64500887/992999
and the following in the file where the config is needed

```
conf = ConfigFactory.factory()
```

"""

from collections import OrderedDict
from os import environ
from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine

# .env file stored at project root
dotenv_path = Path(__file__).parent.parent.resolve() / ".env"
load_dotenv(dotenv_path=dotenv_path)


class ConfigFactory(object):
    def factory():
        env = environ.get("ENV", "DEVELOPMENT")
        if env == "PRODUCTION":
            return Production()
        elif env == "DEVELOPMENT":
            return Development()


class Config:
    """Base Config"""

    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8009

    # Checks for remote updates on the server
    # TODO: feels like we need to run as a check that looks for an update time stamp but does not update the table
    # until the server data changes
    REFRESH_INTERVAL = 5 * 60 * 1000  # milliseconds

    COLS = OrderedDict(
        {
            "ward_code": "Ward",
            "bed_code": "Bed code",
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
            "bed_empty": "Empty",
            "team": "Side",
            "discharge_ready_1_4h": "Discharge",
            "vent_type_1_4h": "Ventilation",
        }
    )

    COLS_FULL = ["bay", "bed", "name", "mrn", "admission_age_years", "sex", "wim_1"]
    # COLS_FULL = {i:COLS[i] for i in COLS_FULL}

    COLS_SIDEBAR = ["bay", "bed", "name", "team"]
    # COLS_SIDEBAR = {i:COLS[i] for i in COLS_SIDEBAR}

    COL_NAMES = [{"name": v, "id": k} for k, v in COLS.items()]

    SKELETON_DATA_SOURCE = Path("data/skeleton.csv")
    ETR_COLUMNS = Path("data/external/etr-columns.csv")
    ETR_DATA = Path("data/external/etr.csv")
    GOV_UK_ENGINE = create_engine("sqlite:///data/gov.db")


class Production(Config):
    DEV = False

    DEV_HYLODE = False
    # Use the IP address b/c slow on DNS resolution
    # e.g. HYLODE_ICU_LIVE = 'http://uclvlddpragae08:5006/icu/live/T06/ui'
    # sitrep data
    HYLODE_ICU_LIVE = "http://172.16.149.205:5006/icu/live/{ward}/ui"
    # census data
    HYLODE_EMAP_CENSUS = "http://172.16.149.205:5006/emap/census/{ward}/"

    DEV_USER = True
    USER_DATA_SOURCE = Path("data/user_edits.csv")


class Development(Config):
    DEV = True
    DEV_HYLODE = True
    HYLODE_ICU_LIVE = "data/icu_{ward}.json"
    HYLODE_EMAP_CENSUS = "data/census_{ward}.json"

    DEV_USER = True
    USER_DATA_SOURCE = "data/user_edits.csv"


header = dbc.Container(
    dbc.Row(
        [
            # dbc.Col([
            #             html.I(className="fa fa-lungs-virus"),
            #             ], md=1),
            dbc.Col(
                [
                    dbc.NavbarSimple(
                        children=[
                            dbc.NavItem(dbc.NavLink("ICU", href="/sitrep")),
                            dbc.NavItem(dbc.NavLink("ED", href="/ed")),
                            dbc.NavItem(dbc.NavLink(["COVID"], href="/covid")),
                        ],
                        brand="UCLH Critical Care Sitrep",
                        brand_href="/",
                        brand_external_link=True,
                        color="primary",
                        dark=True,
                        sticky=True,
                    ),
                ]
            ),
        ]
    ),
    fluid=True,
)

nav = dbc.Container(fluid=True)
# nav = dbc.Nav([
#     dbc.NavItem(dbc.NavLink('Sitrep', href='/sitrep')),
#     dbc.NavItem(dbc.NavLink('COVID', href='/covid')),
#     ])

footer = dbc.Container(fluid=True)
