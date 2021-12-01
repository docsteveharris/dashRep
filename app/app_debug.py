
"""
For debugging
"""
from config import ConfigFactory
from dash import dash_table as dt
from dash import dcc, html
import wrangle as wng

conf = ConfigFactory.factory()

df_hylode = wng.get_hylode_data(conf.HYLODE_DATA_SOURCE, dev=conf.DEV_HYLODE)

debug = html.Div([
    dt.DataTable(
        id='debug',
        columns = [{"name": i, "id": i} for i in df_hylode.columns],
        data=df_hylode.to_dict('records'),
        filter_action="native",
        sort_action="native"

        )
])

