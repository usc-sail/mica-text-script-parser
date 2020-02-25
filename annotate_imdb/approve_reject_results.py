import pandas as pd
import re
import numpy as np
from textdistance import levenshtein

def normalize_movie_title(title):
    norm_regex = r"[^a-z0-9&]+"
    start_tokens = ["a", "the", "an"]
    end_tokens = ["the", "script", "a", "an"]

    title_tokens = re.split(norm_regex, title.lower())

    title_i, title_j = 0, len(title_tokens) - 1

    while title_i < len(title_tokens) and title_tokens[title_i] in start_tokens:
        title_i += 1

    while title_j >= 0 and title_tokens[title_j] in end_tokens:
        title_j -= 1

    title_tokens = title_tokens[title_i: title_j + 1]

    title_tokens = ["and" if x == "&" else x for x in title_tokens]

    norm_title = "".join(title_tokens)

    return norm_title

def is_equal(title1, title2):
    norm_title1 = normalize_movie_title(title1)
    norm_title2 = normalize_movie_title(title2)
    distance = levenshtein(norm_title1, norm_title2)

    return norm_title1 == norm_title2 or norm_title1 in norm_title2 or norm_title2 in norm_title1 or distance <= 2

def analyze_results():
    filepath = "Batch_3853802_batch_results.csv"
    results_df = pd.read_csv(filepath)

    imdb_regex = r"imdb.com/title/tt\d{7}"

    results_df["is_imdb"] = results_df["Answer.imdb"].apply(lambda imdb_url: re.search(imdb_regex, imdb_url) is not None)
    results_df["same_title"] = results_df.apply(lambda row: is_equal(row["Input.movie"], row["Answer.title"]), axis = 1)

    n = results_df.shape[0]
    n_url_correct = results_df["is_imdb"].sum()
    n_url_wrong = (~results_df["is_imdb"]).sum()
    n_url_correct_and_same_title = (results_df["is_imdb"] & results_df["same_title"]).sum()
    n_url_correct_and_diff_title = (results_df["is_imdb"] & ~results_df["same_title"]).sum()

    url_correct_and_diff_title = results_df["is_imdb"] & ~results_df["same_title"]
    url_correct_and_same_title = results_df["is_imdb"] & results_df["same_title"]

    count_series = results_df[url_correct_and_same_title].groupby("HITId").count()["HITTypeId"]
    n_movies_two_annotations = (count_series == 2).sum()
    n_movies_one_annotations = (count_series == 1).sum()

    two_annotation_index = count_series.index[count_series == 2].values
    n_movies_agree = 0
    n_movies_disagree = 0

    udf = results_df.loc[url_correct_and_same_title]
    for _, movie_df in udf[udf["HITId"].isin(two_annotation_index)].groupby("HITId"):
        imdb1, imdb2 = movie_df["Answer.imdb"].values
        
        imdb1_i = re.search(imdb_regex, imdb1).span()[1]
        imdb1_id = imdb1[imdb1_i - 7: imdb1_i]

        imdb2_i = re.search(imdb_regex, imdb2).span()[1]
        imdb2_id = imdb2[imdb2_i - 7: imdb2_i]

        if imdb1_id == imdb2_id:
            n_movies_agree += 1
        else:
            n_movies_disagree += 1

    print("{} total annotations".format(n))
    print("{} total annotations = {} wrong + {} correct a/c URL Type".format(n, n_url_wrong, n_url_correct))
    print("{} total correct URL Type annotations = {} wrong + {} correct a/c Equality of Input Movie title and Answer Movie title".format(n_url_correct, n_url_correct_and_diff_title, n_url_correct_and_same_title))
    print("{} total correct URL Type AND Equal titles = {} 2x annotations + {} 1x annotations".format(n_url_correct_and_same_title, n_movies_two_annotations, n_movies_one_annotations))
    print("{} 2x movies correct URL Type AND Equal titles = {} agree + {} disagree".format(n_movies_two_annotations, n_movies_agree, n_movies_disagree))
    print()

    print("Correct URL , Different Title =>")
    for index, row in results_df[url_correct_and_diff_title].iterrows():
        print("\t{:4d}. {:50s} {:50s}".format(index, row["Input.home_url"], row["Answer.imdb"]))
    print()

def approve_or_reject():
    # 806, 807 & 1410, 1411 should be discarded

    filepath = "Batch_3853802_batch_results.csv"
    output_filepath = "Batch_3853802_batch_results_ar.csv"

    results_df = pd.read_csv(filepath)
    imdb_regex = r"imdb.com/title/tt\d{7}"
    to_approve = [618, 806, 807, 843, 845, 917, 957, 983, 1410, 1411, 1444, 1452, 1490, 1531]

    is_imdb = results_df["Answer.imdb"].apply(lambda imdb_url: re.search(imdb_regex, imdb_url) is not None)
    is_same_title = results_df.apply(lambda row: is_equal(row["Input.movie"], row["Answer.title"]), axis = 1)
    approve_index_mask = results_df.index.isin(to_approve)

    results_df["Approve"] = np.nan
    results_df["Reject"] = np.nan

    approve_mask = approve_index_mask | (is_imdb & is_same_title)
    reject_imdb_mask = ~approve_index_mask & ~is_imdb
    reject_title_mask = ~approve_index_mask & is_imdb & ~is_same_title
    reject_mask = reject_imdb_mask | reject_title_mask

    results_df.loc[approve_mask, "Approve"] = "x"
    results_df.loc[reject_imdb_mask, "Reject"] = "We are sorry to inform you that your annotation was rejected because the IMDb url submitted did not link to an IMDb page."
    results_df.loc[reject_title_mask, "Reject"] = "We are sorry to inform you that your annotation was rejected because the IMDb url submitted did not link to the correct movie"

    results_df.to_csv(output_filepath)

    workers_approved = set(results_df.loc[approve_mask, "WorkerId"].unique())
    workers_rejected = set(results_df.loc[~approve_mask, "WorkerId"].unique())

    print("#workers in approved HITs = {}".format(len(workers_approved)))
    print("#workers in rejected HITs = {}".format(len(workers_rejected)))
    print("#workers in both a&r HITS = {}".format(len(workers_approved.intersection(workers_rejected))))

    workers_ar = list(workers_approved.intersection(workers_rejected))
    print("Workers in both approve and reject list & #approve < #reject =>\n")
    for worker in workers_ar:
        worker_df = results_df.loc[results_df["WorkerId"] == worker]
        n = worker_df.shape[0]
        n_approve = worker_df["Approve"].notna().sum()
        n_reject  = worker_df["Reject"].notna().sum()
        if n_approve < n_reject:
            print("\tWorker {:15s}: {:2d} HITs = {:2d} Approve + {:2d} Reject".format(worker, n, n_approve, n_reject))

if __name__ == "__main__":
    # analyze_results()
    approve_or_reject()