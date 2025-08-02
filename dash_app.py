import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import polars as pl
import pandas as pd
from rank_choice import tabulate, ranked_pairs, process_dash_df
from io import StringIO
import dash_dataframe_table
import dash_bootstrap_components as dbc
from contextlib import redirect_stdout


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div(
    [
        html.H1("Ranked Choice Voting Analyzer"),
        html.Div(
            [
                html.H3("Paste Data Here:"),
                dcc.Textarea(
                    id="text-input",
                    value="",
                    style={"width": "100%", "height": 300},
                    placeholder='Paste your data here. First column should be "Name" (voter), subsequent columns are options with ranks.',
                    persistence=True,
                    persistence_type="session",
                ),
            ]
        ),
        dbc.InputGroup(
            style={"width": "35%", "margin": "auto"},
            children=[
                dbc.Button("Analyze Data", id="analyze-button", n_clicks=0),
                dbc.Select(
                    id="model-dropdrown",
                    options=["Ranked Pairs", "Instant Run Off"],
                    value="Ranked Pairs",
                ),
            ],
        ),
        html.Hr(),
        html.Div(id="output-container"),
    ]
)


@app.callback(
    Output("output-container", "children"),
    Input("analyze-button", "n_clicks"),
    State("text-input", "value"),
    State(
        "model-dropdrown",
        "value",
    ),
)
def update_output(n_clicks, csv_data, model):
    if n_clicks > 0 and csv_data:
        myio = StringIO(csv_data)
        df = pd.read_csv(myio, sep="\t")
    else:
        return dash.no_update
    df = process_dash_df(df)
    with redirect_stdout(StringIO()) as f:
        if model == "Ranked Pairs":
            winner = ranked_pairs(df)
            return [dcc.Markdown(f"## Winner - {winner}"), html.Pre(f.getvalue())]
        else:
            winner_df = tabulate(df)
            return [
                dbc.Table.from_enhanced_dataframe(winner_df.to_pandas()),
                html.Pre(f.getvalue()),
            ]


if __name__ == "__main__":
    app.run_server(debug=True)
