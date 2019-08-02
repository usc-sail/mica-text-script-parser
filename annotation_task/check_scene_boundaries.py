# author - Sabyasachee

import numpy as np
from script_parser import script_parser
from calc_gold_annotations import calc_gold_annotations
from utils import read_annotation_movies

def check_scene_boundaries():
    # perform error analysis on scene boundaries (class = S)
    # print the number of true positives, false positives and false negatives
    # print all lines of false positives and false negatives

    movies, begs, ends = read_annotation_movies()
    gold_labels = calc_gold_annotations()

    examples = []
    mica_labels = []
    for movie, beg, end in zip(movies, begs, ends):
        filepath = "../../mica-scripts/scripts_txt/{}.txt".format(movie)
        labels = script_parser(filepath, write = False)
        mica_labels.append(labels[beg - 1:end])
        examples.extend(open(filepath).read().split("\n")[beg - 1:end])

    M = np.array(list("".join(mica_labels)))
    G = np.array(list("".join(gold_labels)))
    examples = np.array(examples)

    print("TP: #(gold  = S, mica  = S) = {}".format(np.sum((G == 'S') & (M == 'S'))))
    print("FN: #(gold  = S, mica != S) = {}".format(np.sum((G == 'S') & (M != 'S'))))
    print("FP: #(gold != S, mica  = S) = {}\n\n".format(np.sum((G != 'S') & (M == 'S'))))

    tp_examples = examples[(G == 'S') & (M == 'S')]
    fn_examples = examples[(G == 'S') & (M != 'S')]
    fp_examples = examples[(G != 'S') & (M == 'S')]

    print("FP examples =>")
    for i, example in enumerate(fp_examples):
        print("\t{:3d}. {}".format(i + 1, example))
    print("\n\n\n")

    print("FN examples =>")
    for i, example in enumerate(fn_examples):
        print("\t{:3d}. {}".format(i + 1, example))
    print("\n\n\n")

if __name__ == "__main__":
    check_scene_boundaries()