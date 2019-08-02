# author - Sabyasachee

import re
import os
import sys
import numpy as np
from collections import Counter

def count_indent_distribution(verbose = False):
    # print distribution of number of movies to number of indents
    # number of indents of a movie script is the minimum number of indents that cover atleast 95% of all lines
    # if verbose is set, also print 5 random movies corresponding to each number of indents
    # 
    # return n_indents_to_movies dictionary
    # n_indents_to_movies is mapping between number of indents to list of movies

    np.random.seed(1)

    movies = open("data/movies.txt").read().strip().split("\n")
    n_indents_to_movies = dict()

    for movie in movies:
        filepath = "../../mica-scripts/scripts_txt/{}.txt".format(movie)
        lines = open(filepath).read().split("\n")
        lines = [line for line in lines if line.strip()]
        lines = [line.replace("\t","    ") for line in lines]
        n_total_lines = len(lines)

        indents = [re.match(r"^[\s]*", line).span()[1] for line in lines]
        indent_n_lines_tuples = Counter(indents).items()
        indent_n_lines_tuples = sorted(indent_n_lines_tuples, key = lambda tup: tup[1], reverse = True)
        n_indents = 0
        cumul_n_lines = 0

        for _, n_lines in indent_n_lines_tuples:
            cumul_n_lines += n_lines
            if cumul_n_lines > 0.95*n_total_lines:
                n_indents += 1
                break
            n_indents += 1
        
        if n_indents == 0:
            print(movie, indent_n_lines_tuples)
            print(cumul_n_lines, 0.95)
            sys.exit(0)

        if n_indents not in n_indents_to_movies:
            n_indents_to_movies[n_indents] = []
        n_indents_to_movies[n_indents].append(movie)

    if verbose:
        print(f"#unique indent distribution for 95% of lines in screenplay\n")

        print(f"\t\t{'INDENTS':8s}\t{'FILES':8s}\t{'PERCENT':8s}\tMOVIES")
        n_indents_list = sorted(list(n_indents_to_movies.keys()))

        for n_indents in n_indents_list:
            n_movies = len(n_indents_to_movies[n_indents])
            percentage = 100*n_movies/len(movies)
            indent_movies = np.array(n_indents_to_movies[n_indents])
            random_movies = np.random.choice(indent_movies, size = min(5, indent_movies.size), replace = False)
            print(f"\t\t{n_indents:8d}\t{n_movies:8d}\t{percentage:8.2f}%\t{', '.join(random_movies)}")
        print()

    return n_indents_to_movies

if __name__ == "__main__":
    count_indent_distribution(verbose = True)
