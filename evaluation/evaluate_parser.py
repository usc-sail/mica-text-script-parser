# original author: Sabyasachee
# modified by: Sandeep

import numpy as np
from calc_gold_annotations import calc_gold_annotations
from utils import read_annotation_movies, calc_score
import time
import sys
import os
import argparse


# PROCESS ARGUMENTS
def read_args():
	parser = argparse.ArgumentParser(description='Script that evaluates movie script parser')
	parser.add_argument("-d", "--dir", help="Path to directory containing parsed output tags", required=True)
	args = parser.parse_args()
	return os.path.abspath(args.dir)


def evaluate_mica():
    # print precision, recall and F1 scores for mica labels against gold labels for dialogue (class = D), 
    # character (class = C) and scene boundaries (class = S)

    movies, begs, ends = read_annotation_movies()
    mica_labels = []
    eval_list = ['D', 'C', 'S', 'T', 'N', 'E']

    for movie, beg, end in zip(movies, begs, ends):
        output_tag_path = parser_noindent_dir + '/' + movie + '_tags.txt'
        labels = np.genfromtxt(output_tag_path, dtype=str, delimiter='\n')
        labels = ''.join(labels).replace('0', ' ')
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

    for class_id in eval_list:
    	prec_val, rec_val, f1_val = calc_score(G, M, class_id)
    	print(class_id + ": prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_val, rec_val, f1_val))

if __name__ == "__main__":
    parser_noindent_dir = read_args()
    evaluate_mica()