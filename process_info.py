import pandas as pd
import re
from settings import DATA_FOLDER
import os
import numpy as np

info_filepath = os.path.join(DATA_FOLDER, "info.csv")
info2_filepath = os.path.join(DATA_FOLDER, "info2.csv")

info_df = pd.read_csv(info_filepath, index_col = 0)
imdb_urls = info_df.loc[~info_df["imdb"].isna(), "imdb"].values
print("{} imdb urls\n".format(len(imdb_urls)))

regex_pattern = r"^((http)|(https))://((www.)|(us.))?imdb.com/((title/tt)|(Title\?))\d{7}"
n = 0
matched_urls = []

print("imdb regex = {}\n".format(regex_pattern))
print("unmatched urls = ")
for imdb_url in imdb_urls:
    if re.match(regex_pattern, imdb_url):
        matched_urls.append(imdb_url)
        n += 1
    else:
        print("\t", imdb_url)

print()
print("%matched = {:.2f}%\n".format(100*n/len(imdb_urls)))

info_df["text_file"] = np.nan
info_df["parsed_file"] = np.nan

for index, row in info_df.iterrows():
    file = row["file"]
    uuid, ext = file.split("/")[-1].split(".")
    text_file = os.path.join(DATA_FOLDER, "scripts_text/{}.txt".format(uuid))
    parsed_file = os.path.join(DATA_FOLDER, "scripts_parsed/{}.txt".format(uuid))

    if os.path.exists(text_file):
        info_df.loc[index, "text_file"] = text_file
    if os.path.exists(parsed_file):
        info_df.loc[index, "parsed_file"] = parsed_file

print("{} text scripts".format(info_df["text_file"].notna().sum()))
print("{} parsed scripts\n".format(info_df["parsed_file"].notna().sum()))

info_df["imdb2"] = np.nan
n_movies = 0
n_movies_and_imdb = 0
n_movies_and_parse = 0
n_movies_and_imdb_and_parse = 0

for movie, movie_df in info_df.groupby("movie"):
    n_movies += 1
    imdb_urls = movie_df.loc[(movie_df["source"] == "dailyscript") & (movie_df["imdb"].notna()), "imdb"].values
    imdb_ids = set()
    for url in imdb_urls:
        match = re.match(regex_pattern, url)
        if match:
            imdb_id = url[:match.span()[1]][-7:]
            imdb_ids.add(imdb_id)
    
    if movie_df["parsed_file"].notna().sum() > 0:
        n_movies_and_parse += 1

    if len(imdb_ids) == 1:
        n_movies_and_imdb += 1
        info_df.loc[info_df["movie"] == movie, "imdb2"] = "https://www.imdb.com/title/tt{}".format(imdb_ids.pop())

        if movie_df["parsed_file"].notna().sum() > 0:
            n_movies_and_imdb_and_parse += 1

print("{} movies".format(n_movies))
print("{} movies have imdb urls".format(n_movies_and_imdb))
print("{} movies have parsed scripts".format(n_movies_and_parse))
print("{} movies have imdb urls and parsed scripts".format(n_movies_and_imdb_and_parse))

info_df.sort_values("movie", inplace = True)
info_df.index = pd.RangeIndex(info_df.shape[0], name = "id")
info_df.to_csv(info2_filepath)