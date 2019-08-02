# author - Sabyasachee
# note the movies printed are not the ones used.

import os
import re
import numpy as np
from count_indent_distribution import count_indent_distribution
from prepare_for_annotation import prepare_for_annotation


def create_annotation_files():
    # print the annotation movies and the beginning and ending range
    # 
    # n_indents_range_n_files is list of 3-tuples - (lo, hi, n_files)
    # n_files is the number of files to choose randomly from files in mica_scripts_dir whose number of indents lies between lo and hi
    # number of indents is the minimum number of indents required to cover atleast 95% of lines
    # 
    # for all files with number of indents in [lo, hi], we choose an excerpt of 250 non empty lines that has atleast lo unique indents
    # we choose n_files such files and prepare them for annotation
    # the annotation files are saved in annotations/templates/

    np.random.seed(0)

    n_indents_to_movies = count_indent_distribution()
    n_indents_range_n_files = [(1,1,5), (2,2,5), (3,3,5), (4,4,5), (5,5,2), (6,6,2), (7,7,2), (8,8,2), (9,9,2),(10,20,5), (20,60,5)]
    n_lines = 250

    for lo_n_indents, hi_n_indents, n_files in n_indents_range_n_files:
        movies = []
        for n_indents in range(lo_n_indents, hi_n_indents + 1):
            if n_indents in n_indents_to_movies:
                movies.extend(n_indents_to_movies[n_indents])
        
        movies = np.array(movies)
        movies.sort()
        movies = np.random.permutation(movies)
        good_movie_start_end_indices = []

        for movie in movies:
            any_good_start = False
            
            filepath = "../../mica-scripts/scripts_txt/{}.txt".format(movie)
            screenplay = open(filepath, "r").read().split("\n")
            starts = np.arange(len(screenplay) - n_lines)
            starts = np.random.permutation(starts)

            for start in starts:
                end = start
                unique_indents = set()
                n_non_empty_lines = 0

                while end < len(screenplay) and n_non_empty_lines != n_lines:
                    line = screenplay[end].replace("\t","    ")
                    if line.strip():
                        n_non_empty_lines += 1
                        indent = re.match(r"^[\s]*", line).span()[1]
                        unique_indents.add(indent)
                    end += 1

                if len(unique_indents) >= lo_n_indents:
                    any_good_start = True
                    break

            if any_good_start:
                good_movie_start_end_indices.append((movie, start, end))
                if len(good_movie_start_end_indices) == n_files:
                    break

        print(f"N_INDENT_RANGE = [{lo_n_indents:2d},{hi_n_indents:2d}]")
        for movie, start, end in good_movie_start_end_indices:
            print(f"\t\t{movie:30s}  [{start:5d}, {end:5d}]")
            # script_filepath = "../mica-scripts/scripts_txt/{}.txt".format(movie)
            # annotation_filepath = "annotations/new_templates/{}.csv".format(movie)
            # prepare_for_annotation(script_filepath, annotation_filepath, start, end)
        print()

if __name__ == "__main__":
    create_annotation_files()
