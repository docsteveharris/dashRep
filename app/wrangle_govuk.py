import arrow
import pandas as pd
import plotly.express as px
import requests
from config import ConfigFactory

conf = ConfigFactory.factory()



engine = conf.GOV_UK_ENGINE
YESTERDAY = str(arrow.now().shift(days=-1).format("YYYY-MM-DD"))
URL_HOSP_CASES = f"https://coronavirus.data.gov.uk/api/v2/data?areaType=nhsTrust&release={YESTERDAY}&metric=hospitalCases&format=json"

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
    "RAL": "Royal Free",
    "RAP": "North Middlesex",
    "RKE": "Whittington",
    "RRP": "Barnet",
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




def request_gov_uk(url, table, engine) -> pd.DataFrame:
    """
    Import COVID information as per the gov.uk API here
    but checks to see if the same request has already been run
    url: API connection
    table: table to store data in local SQLite
    conn: connection to local db for storing data and logging requests
    """
    with engine.connect() as conn:
        requests_df = pd.read_sql("requests_log", conn)

        if url in requests_df.request.values:
            df = pd.read_sql(table, conn)

        else:
            response = requests.get(url)
            df = pd.json_normalize(response.json(), record_path="body")
            df.to_sql(table, conn, if_exists="replace")

            request_log = pd.DataFrame(
                {"request": [url], "table": [table], "request_ts": [str(arrow.now())]}
            )
            request_log.to_sql("requests_log", conn, if_exists="append")
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


TRUST_INFO = prepare_trust_info()
df = request_gov_uk(URL_HOSP_CASES, "hosp_cases", engine)
df = clean_hosp_cases(df, TRUST_INFO)
HOSP_CASES = df
