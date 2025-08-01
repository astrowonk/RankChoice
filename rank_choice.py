import polars as pl
import random
import itertools
import networkx as nx

from hashlib import md5


def process_csv(csv_file, drop_nulls=True):
    csv_books = (
        pl.read_csv(csv_file)
        .unpivot(index="Name")
        .with_columns(pl.col("value").cast(pl.Int64))
    )
    if not drop_nulls:
        return (
            csv_books.fill_null(0)
            .rename({"Name": "voter", "variable": "option"})
            .with_columns(rank=pl.col("value").max() + 1 - pl.col("value"))
        )
    return (
        csv_books.drop_nulls()
        .rename({"Name": "voter", "variable": "option"})
        .with_columns(rank=pl.col("value").max() + 1 - pl.col("value"))
    )


def make_one_fake_voter(voter: str, options: list):
    random.shuffle(options)
    out = [
        {
            "voter": voter,
            "option": x,
            "rank": i + 1,
        }
        for i, x in enumerate(options)
    ]
    r = random.randint(2, 5)
    return out[:r]


def make_all_fake_data2(n=1000, n_options=5):
    options = [md5(random.randbytes(10)).hexdigest()[:3] for i in range(n_options)]
    out = []
    for voter in range(n):
        out.extend(
            make_one_fake_voter(str(voter), options=options),
        )
    return pl.DataFrame(out)


def process_df(df):
    proc_df = df.filter(pl.col("rank").eq(pl.col("rank").min().over(pl.col("voter"))))
    out_df = proc_df.group_by("option").agg(pl.col("voter").count()).sort("voter")
    # print(out_df)
    remove_str = out_df.item(
        0,
        0,
    )
    to_remove = pl.col("option").eq(remove_str)
    print(f"Will Remove {remove_str}")
    if len(out_df) == 2:
        winner = out_df.item(
            1,
            0,
        )
        print(f"Winner {winner}")
    cleaned_df = df.remove(to_remove)
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
    # 804-727-8700df.filter(pl.col('rank')).group_by('option').agg(pl.col('voter').)
    for pair in itertools.combinations(df["option"].unique().to_list(), 2):
        res = (
            df.filter(pl.col("option").is_in(pair))
            .filter(pl.col("rank").eq(pl.col("rank").min().over(pl.col("voter"))))
            .group_by("option")
            .agg(pl.col("voter").count())
            .with_columns(
                voter_pct=pl.col("voter") / pl.col("voter").sum(),
                votes_opponent=pl.col("voter").sum() - pl.col("voter"),
            )
            .with_columns(
                vote_margin=pl.col("voter").cast(pl.Int64)
                - pl.col("votes_opponent").cast(pl.Int64)
            )
            .sort(["vote_margin", "votes_opponent"], descending=[True, False])
            .with_columns(pair=pl.col("option").str.join("____"))
        )

        if res.shape[0] == 2:
            out_pairs.append(res.head(1))
            if res["voter_pct"].item(0) == 0.5:
                print("A Tie", res["pair"].item(0))
    combined = (
        pl.concat(out_pairs)
        .sort("voter_pct", descending=True)
        .remove(pl.col("voter_pct").eq(0.5))
    )  # remove ties
    print(combined)
    edges = [tuple(x.split("____")) for x in combined["pair"].to_list()]
    mynetwork = nx.DiGraph()
    for i, edge in enumerate(edges):
        a, b = edge
        mynetwork.add_edge(a, b)
        if len(list(nx.simple_cycles(mynetwork))) > 0:
            print(
                f"edge number {i} at {a, b} with pct {combined['voter_pct'][i]:.3%} would create a cycle {list(nx.simple_cycles(mynetwork))}"
            )
            mynetwork.remove_edge(a, b)

    print(
        "winner",
        [node for node in mynetwork.nodes if mynetwork.in_degree(node) == 0][0],
    )
    nx.draw_networkx(mynetwork, pos=nx.circular_layout(mynetwork))
    return mynetwork
