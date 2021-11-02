from os import environ
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from collections import OrderedDict

# .env file stored at project root
dotenv_path = Path(__file__).parent.parent.resolve() / '.env'
load_dotenv(dotenv_path=dotenv_path)

# as per https://stackoverflow.com/a/64500887/992999
class ConfigFactory(object):
    def factory():
        env = environ.get('ENV', 'DEVELOPMENT') 
        if env == 'PRODUCTION':
            return Production()
        elif env == 'DEVELOPMENT':
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
            'bed_code': 'Bed code',
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


class Production():
    # Use the IP address b/c slow on DNS resolution
    # HYLODE_DATA_SOURCE = 'http://uclvlddpragae08:5006/icu/live/T06/ui'
    DEV_HYLODE = False
    HYLODE_DATA_SOURCE = "http://172.16.149.205:5006/icu/live/T03/ui"
    DEV_USER = True
    USER_DATA_SOURCE = Path("data/user_edits.csv")


class Development():
    DEV_HYLODE = True
    HYLODE_DATA_SOURCE = Path("data/icu.json")

    DEV_USER = True
    USER_DATA_SOURCE = Path("data/user_edits.csv")




