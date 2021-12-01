"""
Principle application file
https://dash.plotly.com/urls
"""

from config import ConfigFactory
from dash import Input, Output, dcc, html
from app_sitrep import sitrep
from app_debug import debug

from app import app

# configurable configuration
conf = ConfigFactory.factory()

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/sitrep":
        return sitrep
    elif pathname == "/debug":
        return debug
    else:
        # TODO return both the code and the page
        return "404"


if __name__ == "__main__":
    app.run_server(port=conf.SERVER_PORT, host=conf.SERVER_HOST, debug=True)
