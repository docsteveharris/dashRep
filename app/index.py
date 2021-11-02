from dash import Input, Output, html, dcc

from app import app
from config import Config
from layouts import sitrep, hello
import callbacks


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/sitrep':
        return sitrep
    elif pathname == '/hello':
        return hello
    else:
        return '404'


if __name__ == "__main__":
    app.run_server(port=Config.SERVER_PORT,
                   host=Config.SERVER_HOST, debug=True)
