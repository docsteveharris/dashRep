"""
Data management for the app
Factored out here to make the flow of the code in the app easier to follow
"""
import pandas as pd
import numpy as np
import json
import requests


def prep_cols_for_table(df, cols):
    list_of_cols = [{"name": i, "id": i}
                    for i in df.columns if i in cols.keys()]
    return list_of_cols


def get_hylode_data(file_or_url: str, dev: bool =False) -> pd.DataFrame:
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
        assert r.status_code==200
        df = pd.DataFrame.from_dict(r.json()['data'])
    else:
        df = pd.read_json(file_or_url)
    return df


def get_user_data(file_or_url: str, dev: bool=False) -> pd.DataFrame:
    """
    Get's user data; stored for now locally as CSV
    :returns:   pandas dataframe with three cols ward,bed,wim_r
    """
    if dev:
        df=pd.read_csv(file_or_url)
        return df
    else:
        raise NotImplementedError

def merge_hylode_user_data(df_hylode, df_user) -> pd.DataFrame:
    """
    """
    res = df_hylode.merge(df_user, how='left', on=['ward_code', 'bed_code'])
    return res


def wrangle_data(df, cols):
    # TODO: refactor this as it does more than one thing
    # Prep and wrangle

    # sort out dates
    df['admission_dt'] = pd.to_datetime(
        df['admission_dt'], infer_datetime_format=True)
    df['admission_dt'] = df['admission_dt'].dt.strftime("%H:%M %d %b %Y")

    # convert LoS to days
    # df['elapsed_los_td'] = pd.to_numeric(df['elapsed_los_td'], errors='coerce')
    df['elapsed_los_td'] = df['elapsed_los_td'] / (60 * 60 * 24)
    df = df.round({'elapsed_los_td': 2})

    # extract bed number from bed_code
    dt = df['bed_code'].str.split('-', expand=True)
    dt.columns = ['bay', 'bed']
    df = pd.concat([df, dt], axis=1)

    df.sort_values(by=['bed'], inplace=True)
    # drop unused cols
    keep_cols = [i for i in df.columns.to_list() if i in cols.keys()]
    keep_cols.sort(key = lambda x: list(cols.keys()).index(x))

    # https://dash.plotly.com/datatable/interactivity
    # be careful that 'id' is not actually the name of a row
    # use this to track rows in the app
    if 'bed_code' not in keep_cols:
        keep_cols[0:0] = ['bed_code']
    df = df[keep_cols]
    df['id'] = df['bed_code']
    df.set_index('id', inplace=True)
    print(df.head())

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
    cols = ['ward_code', 'bed_code', 'wim_r']

    bed = df['bed_code']
    ward = df['ward_code']
    wim_r = df['wim_r']

    # first read from existing source df origin (dfo)
    dfo = pd.read_csv(file_or_url)
    # now filter by new data 
    matching_row = dfo.index[(dfo['ward_code'] == ward) & (dfo['bed_code'] == bed)].to_list()
    # then check if key in source
    # if key then replace
    if len(matching_row) == 1:
        res = dfo.copy()
        res.loc[matching_row, 'wim_r'] = wim_r
    else:
        # else append
        res = dfo.append(df[cols])

    res[cols].to_csv(file_or_url, index=False)
    return True
