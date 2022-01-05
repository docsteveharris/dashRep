from io import StringIO

import arrow
import pandas as pd
import plotly.express as px
import requests
import logging

from config.config import ConfigFactory
conf = ConfigFactory.factory()


engine = conf.GOV_UK_ENGINE
YESTERDAY = str(arrow.now().shift(days=-1).format("YYYY-MM-DD"))
URL_HOSP_CASES = f"https://coronavirus.data.gov.uk/api/v2/data?areaType=nhsTrust&release={YESTERDAY}&metric=hospitalCases&format=json"
URL_CASES_BY_AGE = f"https://api.coronavirus.data.gov.uk/v2/data?areaType=region&areaCode=E12000007&metric=newCasesBySpecimenDateAgeDemographics&format=csv"

# GOV UK dictionaries and lists

TRUSTS_LONDON = [
    "R1H",
    "RRV",
    "RPY",
    "RQM",
    "RQX",
    "RQY",
    "RRP",
    "RRU",
    "RT3",
    "RP6",
    "RV3",
    "RV5",
    "RVR",
    "RWK",
    "RY9",
    "RYJ",
    "RPG",
    "RP4",
    "R1K",
    "RF4",
    "RAL",
    "RAN",
    "RAP",
    "RAS",
    "RAT",
    "RAX",
    "RJ1",
    "RNK",
    "RJ2",
    "RJ6",
    "RJ7",
    "RJZ",
    "RKE",
    "RKL",
    "RYX",
]

SECTORS_LONDON = {
    "QKK": "South East London",
    "QMF": "North East London",
    "QMJ": "North Central London",
    "QRV": "North West London",
    "QWE": "South West London",
}

TRUSTS_NCL = {
    "RAP": "North Middlesex",
    "RKE": "Whittington",
    "RAL": "Royal Free & Barnet",
    # "RRP": "Barnet", # NOTE: this was the mental health trust
    "RRV": "UCLH",
}


def prepare_trust_info():

    cols = pd.read_csv(conf.ETR_COLUMNS)
    cols["colname"] = cols["Field Content"]
    for idx, row in cols.iterrows():
        if row["colname"] == "Null":
            cols.loc[idx, "colname"] = str(row["Column"])

    df = pd.read_csv(conf.ETR_DATA, names=list(cols.colname))

    df.rename(columns={"Organisation Code": "areaCode"}, inplace=True)
    df["inLondon01"] = False
    df.loc[df["areaCode"].isin(TRUSTS_LONDON), "inLondon01"] = True

    df["inNCL01"] = False
    df.loc[df["areaCode"].isin(TRUSTS_NCL), "inNCL01"] = True

    df2 = pd.DataFrame.from_dict(TRUSTS_NCL, orient="index", columns=["shortName"])
    df = df.merge(df2, how="left", left_on="areaCode", right_index=True)

    df2 = pd.DataFrame.from_dict(SECTORS_LONDON, orient="index", columns=["sectorName"])
    df = df.merge(
        df2, how="left", left_on="High Level Health Geography", right_index=True
    )
    return df


def request_gov_uk(url, table, engine, format='json') -> pd.DataFrame:
    """
    Import COVID information as per the gov.uk API here
    but checks to see if the same request has already been run
    url: API connection
    table: table to store data in local SQLite
    conn: connection to local db for storing data and logging requests
    format: json or csv
    """
    with engine.connect() as conn:
        req_df = pd.read_sql('requests_log', conn, parse_dates=['request_ts'])
        
        request_exists = True if url in req_df.request.values else False
        request_max_ts = req_df.loc[req_df.request == URL_CASES_BY_AGE, 'request_ts'].max() 
        request_recent = True if request_max_ts > arrow.now().shift(days=-1) else False
        
        if request_exists and request_recent:
            logging.info(f'--- using cached data for {table}')
            # sql call at end of function        
        else:
            logging.info(f'--- requesting from gov.uk for {table}')
            response = requests.get(url)
            if format == 'json':
                df = pd.json_normalize(response.json(), record_path="body")
            elif format == 'csv':
                df = pd.read_csv(StringIO(response.text))
            else:
                raise NotImplementedError
            df.to_sql(table, conn, if_exists='replace')

            request_log = pd.DataFrame({
                'request': [url],
                'table': [table],
                'request_ts': [str(arrow.now())]
            })
            request_log.to_sql('requests_log', conn, if_exists='append')
            
        df = pd.read_sql(table, conn, parse_dates=['date'])
    return df


def clean_hosp_cases(df, TRUST_INFO):
    """
    Clean hosp cases
    df : data frame of hospital cases
    TRUST_INFO: data frame of trust information
    """
    trusts_london = TRUST_INFO[TRUST_INFO.inLondon01][
        ["areaCode", "shortName", "sectorName", "inNCL01"]
    ]
    df = df.merge(trusts_london, how="inner", on="areaCode")
    df["date"] = pd.to_datetime(df["date"])
    df.drop(["areaType"], axis=1, inplace=True)
    return df


def clean_popn_cases(df):
    """
    Clean population cases (London)
    df : data frame of population cases by age
    """
    df["date"] = pd.to_datetime(df["date"])
    df.drop(["areaType", "areaCode", "areaType"], axis=1, inplace=True)
    return df


TRUST_INFO = prepare_trust_info()
df = request_gov_uk(URL_HOSP_CASES, "hosp_cases", engine)
df = clean_hosp_cases(df, TRUST_INFO)
HOSP_CASES = df

df = request_gov_uk(URL_CASES_BY_AGE, "cases_by_age", engine, format="csv")
df = clean_popn_cases(df)
CASES_BY_AGE = df
