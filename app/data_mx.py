"""
Data management for the app
Factored out here to make the flow of the code in the app easier to follow
"""
import pandas as pd
import numpy as np


def prep_cols_for_table(df, cols):
    list_of_cols = [{"name": i, "id": i}
                    for i in df.columns if i in cols.keys()]
    return list_of_cols


def read_data(file_or_url: str) -> pd.DataFrame:
    """
    Reads a data.

    :param      file_or_url:  The file or url
    :type       file_or_url:  any valid string path is acceptable

    :returns:   pandas dataframe
    :rtype:     pandas dataframe
    """

    # Read in the data
    return pd.read_json(file_or_url)


def wrangle_data(df, cols):
    # TODO: refactor this as it does more than one thing
    # Prep and wrangle
    df['admission_dt'] = pd.to_datetime(
        df['admission_dt'], infer_datetime_format=True)
    df['admission_dt'] = df['admission_dt'].dt.strftime("%H:%M %d %b %Y")
    df = df[cols.keys()]
    df.sort_values(by='bed_code', inplace=True)

    columns = [{"name": i, "id": i} for i in df.columns if i in cols.keys()]
    for column in columns:
        column['name'] = cols[column['id']]
        if column['id'] == 'admission_dt':
            column['type'] = 'datetime'
    return df


def write_data(data, file_or_url):
    with file_or_url.open('w') as f:
        json.dump(data, f, indent=4)
    return True
