import pandas as pd
import os

info2_filepath = "../data/info2.csv"
input_filepath = "../data/input.csv"

info2_df = pd.read_csv(info2_filepath, index_col = 0)
input_df = info2_df.loc[info2_df["imdb2"].isna() & (info2_df["source"] == "imsdb"), ["movie", "home_url", "movie_url"]]

print("{} rows".format(input_df.shape[0]))
print("{} movies".format(input_df["movie"].unique().shape[0]))

input_df.to_csv(input_filepath)