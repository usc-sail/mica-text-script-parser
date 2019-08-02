# author - Sabyasachee

import numpy as np
from calc_gold_annotations import calc_gold_annotations
from script_parser import script_parser
from utils import read_annotation_movies, calc_score

def evaluate_mica():
    # print precision, recall and F1 scores for mica labels against gold labels for dialogue (class = D), 
    # character (class = C) and scene boundaries (class = S)

    movies, begs, ends = read_annotation_movies()
    mica_labels = []

    for movie, beg, end in zip(movies, begs, ends):
        filepath = "../../mica-scripts/scripts_txt/{}.txt".format(movie)
        labels = script_parser(filepath, write = False)
        labels = labels[beg - 1: end]
        mica_labels.append(labels)
    
    gold_labels = calc_gold_annotations()

    M = "".join(mica_labels)
    G = "".join(gold_labels)

    M = np.array(list(M))
    G = np.array(list(G))
    mask = (G != 'X')
    G = G[mask]
    M = M[mask]

    prec_D, rec_D, f1_D = calc_score(G, M, 'D')
    prec_C, rec_C, f1_C = calc_score(G, M, 'C')
    prec_S, rec_S, f1_S = calc_score(G, M, 'S')
    prec_T, rec_T, f1_T = calc_score(G, M, 'T')
    prec_N, rec_N, f1_N = calc_score(G, M, 'N')
    
    print("D: prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_D, rec_D, f1_D))
    print("C: prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_C, rec_C, f1_C))
    print("S: prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_S, rec_S, f1_S))
    print("T: prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_T, rec_T, f1_T))
    print("N: prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_N, rec_N, f1_N))

if __name__ == "__main__":
    evaluate_mica()  