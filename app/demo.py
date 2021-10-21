from pathlib import Path

import pandas as pd
import dash
import dash_table
from dash import html

DATA_SOURCE = Path('../data/icu.json')

df = pd.read_json(DATA_SOURCE)

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns = [{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    )

if __name__ == "__main__":
    app.run_server(debug=True)
