
"""
Placeholder for ED
"""
from config import ConfigFactory
from dash import dash_table as dt
from dash import dcc, html
import wrangle as wng

conf = ConfigFactory.factory()

df_sitrep = wng.get_hylode_data(conf.HYLODE_ICU_LIVE, dev=conf.DEV_HYLODE)
df_census = wng.get_hylode_data(conf.HYLODE_EMAP_CENSUS, dev=conf.DEV_HYLODE)

ed = html.Div([
    html.H1('Emergency Department data'),
    html.P('Page under construction'),
])

