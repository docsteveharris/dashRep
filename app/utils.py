import collections
import pandas as pd


def deep_update(source, overrides):
    """
    Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    via https://stackoverflow.com/a/30655448/992999
    """
    for key, value in overrides.items():
        if isinstance(value, collections.abc.Mapping) and value:
            # note recursive
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source



def get_dict_from_list(llist, kkey, vval):
    """
    Given a list of dictionaries, and a key:value pair, will return the matching dictionary
    """
    matches = 0
    for ddict in llist:
        if ddict[kkey] == vval:
            res = ddict
            matches += 1
    if matches == 0:
        return {}
    elif matches == 1:
        return res
    else:
        raise ValueError(f"{matches} matches for {kkey}={vval}; expected only 1")


def tbl_compare(df_old: pd.DataFrame, df_new: pd.DataFrame, cols2save: list, idx=['ward_code', 'mrn']):
    """
    compare two dataframes and return a long dataframe with any edits
    must be indexed by ward_code and mrn
    
    :param      dfo:  dataframe old
    :param      dfn:  dataframe new
    :param      idx:  index used to align dataframes
    """

    dfo = df_old.copy()
    dfo.set_index(idx, inplace=True, drop=True)
    dfo = dfo[cols2save]

    dfn = df_new.copy()
    dfn.set_index(idx, inplace=True, drop=True)
    dfn = dfn[cols2save]

    assert all(dfo.columns.sort_values() == dfo.columns.sort_values())

    dfr = dfn.compare(dfo, align_axis=0)
    dfr['compared_at'] = pd.Timestamp.now() 
    dfr.rename(index={'self':'new', 'other':'old'}, inplace=True)
    dfr.reset_index(level=2, inplace=True)
    dfr.rename(columns=dict(level_2='data_source'), inplace=True)

    # convert to long
    dfr = dfr.reset_index().melt(id_vars=['ward_code', 'mrn', 'compared_at', 'data_source'])

    return dfr

  