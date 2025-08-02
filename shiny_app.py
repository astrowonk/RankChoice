# Express

from shiny import reactive
from shiny.express import input, render, ui
from rank_choice import tabulate, ranked_pairs, process_dash_df
from io import StringIO
import pandas as pd
import polars as pl
from contextlib import redirect_stdout

ui.input_text_area('txt_in', 'Paste tab delimited data here:', width='90%', height='300px')
ui.input_select(
    id='select', label='Select an option below:', choices=['Ranked Pairs', 'Instant Run Off']
)

ui.input_action_button('action_button', 'Action')


@reactive.calc
@reactive.event(input.action_button)
def result():
    myio = StringIO(input.txt_in())
    df = pd.read_csv(myio, sep='\t')
    with redirect_stdout(StringIO()) as f:
        if input.select() == 'Ranked Pairs':
            winner = ranked_pairs(process_dash_df(df))
        else:
            winner = tabulate(process_dash_df(df))

    return f.getvalue(), winner


@render.ui
def out_winner():
    if isinstance(result()[1], str):
        return ui.h2(f'Winner: {result()[1]}')


@render.data_frame
def out_df():
    if isinstance(result()[1], pl.DataFrame):
        return result()[1]


@render.code
def out_text():
    return result()[0]
