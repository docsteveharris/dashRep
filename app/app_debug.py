
"""
For debugging
"""
from config import ConfigFactory
from dash import dash_table as dt
from dash import dcc, html
import wrangle as wng

conf = ConfigFactory.factory()

df_sitrep = wng.get_hylode_data(conf.HYLODE_ICU_LIVE, dev=conf.DEV_HYLODE)
df_census = wng.get_hylode_data(conf.HYLODE_EMAP_CENSUS, dev=conf.DEV_HYLODE)

debug = html.Div([
    html.P('Sitrep data only (before joining on to census data'),
    dt.DataTable(
        id='debug',
        columns = [{"name": i, "id": i} for i in df_sitrep.columns],
        data=df_sitrep.to_dict('records'),
        filter_action="native",
        sort_action="native"

        ),
    html.P('Census data only (before joining on to sitrep data'),
    dt.DataTable(
        id='debug',
        columns = [{"name": i, "id": i} for i in df_census.columns],
        data=df_census.to_dict('records'),
        filter_action="native",
        sort_action="native"

        )
])

