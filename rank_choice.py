import polars as pl
import random
import itertools
import networkx as nx


def make_one_fake_voter(voter: str):
    options = ["Blue", "Red", "Green", "Purple", "Yellow"]
    random.shuffle(options)
    if options[0] == "Blue" and random.random() < 0.75:
        rest = ["Green", "Purple", "Yellow"]
        random.shuffle(rest)
        options = ["Blue", "Green"] + rest
    out = [
        {
            "voter": voter,
            "option": x,
            "rank": i + 1,
        }
        for i, x in enumerate(options)
    ]
    r = random.randint(1, 5)
    return out[:r]


def make_all_fake_data2():
    out = []
    for voter in range(1000):
        out.extend(make_one_fake_voter(str(voter)))
    return pl.DataFrame(out)


def process_df(df):
    proc_df = df.filter(pl.col("rank").eq(pl.col("rank").min().over(pl.col("voter"))))
    out_df = proc_df.group_by("option").agg(pl.col("voter").count()).sort("voter")
    # print(out_df)
    cleaned_df = df.remove(
        pl.col("option").eq(
            out_df.item(
                0,
                0,
            )
        )
    )
    return cleaned_df, proc_df, out_df


def tabulate(df):
    cleaned_df, proc_df, out_df = process_df(df)
    while out_df.shape[0] > 2:
        print(out_df)
        print(out_df["voter"].sum())
        cleaned_df, proc_df, out_df = process_df(cleaned_df)
    return out_df


def ranked_pairs(df):
    out_pairs = []
    for pair in itertools.combinations(df["option"].unique().to_list(), 2):
        res = (
            df.filter(pl.col("option").is_in(pair))
            .filter(pl.col("rank").eq(pl.col("rank").min().over(pl.col("voter"))))
            .group_by("option")
            .agg(pl.col("voter").count())
            .with_columns(voter_pct=pl.col("voter") / pl.col("voter").sum())
            .sort("voter_pct", descending=True)
            .with_columns(pair=pl.col("option").str.join("_"))
        )
        out_pairs.append(res.head(1))
    combined = (
        pl.concat(out_pairs)
        .sort("voter_pct", descending=True)
        .remove(pl.col("voter_pct").eq(0.5))
    )  # remove ties
    print(combined)
    edges = [tuple(x.split("_")) for x in combined["pair"].to_list()]
    mynetwork = nx.DiGraph()
    for a, b in edges:
        mynetwork.add_edge(a, b)
        if len(list(nx.simple_cycles(mynetwork))) > 0:
            print(
                f"edge {a, b} would create a cycle {list(nx.simple_cycles(mynetwork))}"
            )
            mynetwork.remove_edge(a, b)

    print(
        "winner",
        [node for node in mynetwork.nodes if mynetwork.in_degree(node) == 0][0],
    )
    nx.draw_networkx(mynetwork)
    return mynetwork
