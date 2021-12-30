"""
Data management for the app
Factored out here to make the flow of the code in the app easier to follow
"""
import json
import warnings

import arrow
import numpy as np
import pandas as pd
import requests
from config import ConfigFactory

conf = ConfigFactory.factory()

VENTILATOR_ACRONYMS = {
    "Room air": "RA",
    "Oxygen": "O2",
    "Ventilated": "MV",
    "Unknown": "?",
    "HFNO": "HF",
    "CPAP": "CP",
}


def prep_cols_for_table(df, cols):
    list_of_cols = [{"name": i, "id": i} for i in df.columns if i in cols.keys()]
    return list_of_cols


def gen_hylode_url(url, ward):
    ward = ward.lower()
    if url == "sitrep":
        res = conf.HYLODE_ICU_LIVE
        res = res.format(ward=ward)
        print(res)
    elif url == "census":
        res = conf.HYLODE_EMAP_CENSUS
        res = res.format(ward=ward)
        print(res)
    else:
        raise NotImplementedError
    return res


def get_hylode_data(file_or_url: str, dev: bool = False) -> pd.DataFrame:
    """
    Reads a data.

    :param      file_or_url:  The file or url
    :type       file_or_url:  any valid string path is acceptable
    :param      dev:    if True works on a file else uses requests and the API

    :returns:   pandas dataframe
    :rtype:     pandas dataframe
    """
    if not dev:
        r = requests.get(file_or_url)
        assert r.status_code == 200
        df = pd.DataFrame.from_dict(r.json()["data"])
    else:
        df = pd.read_json(file_or_url)
    return df


def merge_census_data(
    sitrep: pd.DataFrame, census: pd.DataFrame, dev: bool = False
) -> pd.DataFrame:
    """
    Cleans sitrep info to ensure that only patients currently in census are reported

    :param      sitrep:  dataframe containing sitrep info
    :param      census:  dataframe containing census info

    :returns:   { description_of_the_return_value }
    """
    if dev:
        # MRNs won't be in sycn if dev; just screen on beds
        census = census[["ward_code", "bay_code", "bed_code"]]
        df = census.merge(sitrep, how="left")
    else:
        # WARN?: assumes that mrn does not change *during* the admission
        census = census[["mrn", "ward_code", "bay_code", "bed_code"]]
        # merge on beds and mrn
        df = census.merge(sitrep, how="left")

        chk = merge_census_data(sitrep, census, dev=True).csn.isna().sum()
        if chk:
            # now check that csn is not missing as a way of warning about non-merges
            warnings.warn(
                f"***FIXME: merge sitrep onto census left {chk} beds without data"
            )

    return df


def get_user_data(file_or_url: str, dev: bool = False) -> pd.DataFrame:
    """
    Get's user data; stored for now locally as CSV
    :returns:   pandas dataframe with three cols ward,bed,wim_r
    """
    if dev:
        df = pd.read_csv(file_or_url)
        return df
    else:
        raise NotImplementedError


def get_bed_skeleton(ward: str, file_or_url: str, dev: bool = False) -> pd.DataFrame:
    """
    Gets the ward skeleton.
    Uses the valid_from column to drop invalid teams

    :param      ward:  The ward
    :type       ward:  str

    :returns:   The ward skeleton.
    :rtype:     pd.DataFrame
    """
    if dev or "T03" == ward:
        warnings.warn(
            "***FIXME: need to properly implement a database of ward structures"
        )
        df = pd.read_csv(file_or_url)
        # keep only those rows where valid_to is missing
        df[df["valid_to"].isna()]
        # TODO: check for dups
        df.drop("valid_to", axis=1, inplace=True)
        return df
    else:
        raise NotImplementedError


def merge_hylode_user_data(df_skeleton, df_hylode, df_user) -> pd.DataFrame:
    """
    Merges HYLODE data onto a skeleton for the ward
    This allows blanks (empty) beds to be represented
    Then merges on any user updates
    """
    df = df_skeleton.merge(df_hylode, how="left", on=["ward_code", "bed_code"])
    df = df.merge(df_user, how="left", on=["ward_code", "bed_code"])
    df["bed_empty"] = False
    df.loc[df.name.isnull(), "bed_empty"] = True
    return df


def isots_str2fmt(s: str, format="HH:mm DD MMM YY") -> str:
    """
    Convert from ISO formatted timestamp as string to alternative format
    Handles nulls or NaNs
    """

    if s in ["NaN", np.NaN] or not s:
        return ""
    else:
        return arrow.get(s).format(format)


def wrangle_data(df, cols):
    # TODO: refactor this as it does more than one thing
    # Prep and wrangle

    # sort out dates
    df["admission_dt_str"] = df.loc[:, "admission_dt"].apply(isots_str2fmt)

    # convert LoS to days
    # df['elapsed_los_td'] = pd.to_numeric(df['elapsed_los_td'], errors='coerce')
    df["elapsed_los_td"] = df["elapsed_los_td"] / (60 * 60 * 24)
    df = df.round({"elapsed_los_td": 2})

    # extract bed number from bed_code
    dt = df["bed_code"].str.split("-", expand=True)
    dt.columns = ["bay", "bed"]
    df = pd.concat([df, dt], axis=1)

    df.sort_values(by=["bed"], inplace=True)
    # drop unused cols
    keep_cols = [i for i in df.columns.to_list() if i in cols.keys()]
    keep_cols.sort(key=lambda x: list(cols.keys()).index(x))

    # https://dash.plotly.com/datatable/interactivity
    # be careful that 'id' is not actually the name of a row
    # use this to track rows in the app
    if "bed_code" not in keep_cols:
        keep_cols[0:0] = ["bed_code"]
    df = df[keep_cols]
    df["id"] = df["bed_code"]
    df.set_index("id", inplace=True, drop=False)

    return df


def select_cols(df: pd.DataFrame, keep_cols: list):
    """
    Returns a filtered (by cols) version of the dataframe

    :param      df:         a dataframe
    :param      keep_cols:  a list of column names

    :returns:   a filtered (selected) dataframe
    """
    return df[keep_cols]


def write_data(df: pd.DataFrame, file_or_url: str):
    """
    :df: dataframe from app, should be single row
    :file_or_url: target dataframe as csv
    """
    cols = ["ward_code", "bed_code", "wim_r"]

    bed = df["bed_code"]
    ward = df["ward_code"]
    wim_r = df["wim_r"]

    # first read from existing source df origin (dfo)
    dfo = pd.read_csv(file_or_url)
    # now filter by new data
    matching_row = dfo.index[
        (dfo["ward_code"] == ward) & (dfo["bed_code"] == bed)
    ].to_list()
    # then check if key in source
    # if key then replace
    if len(matching_row) == 1:
        res = dfo.copy()
        res.loc[matching_row, "wim_r"] = wim_r
    else:
        # else append
        res = dfo.append(df[cols])

    res[cols].to_csv(file_or_url, index=False)
    return True
