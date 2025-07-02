import marimo

__generated_with = "0.14.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import networkx as nx
    return (nx,)


@app.cell
def _():
    from rank_choice import make_all_fake_data2, tabulate, ranked_pairs
    return make_all_fake_data2, ranked_pairs, tabulate


@app.cell
def _(make_all_fake_data2):
    df = make_all_fake_data2()
    return (df,)


@app.cell
def _(df, tabulate):
    tabulate(df)
    return


@app.cell
def _(df, ranked_pairs):
    G = ranked_pairs(df)
    return (G,)


@app.cell
def _(G):
    G
    return


@app.cell
def _(G, nx):
    nx.draw_networkx(G)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
