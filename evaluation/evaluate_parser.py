# original author: Sabyasachee
# modified by: Sandeep

import numpy as np
from calc_gold_annotations import calc_gold_annotations
from utils import read_annotation_movies, calc_score
import time
import sys
import os
import argparse
from sklearn.metrics import confusion_matrix, precision_score, recall_score


# PROCESS ARGUMENTS
def read_args():
    parser = argparse.ArgumentParser(description='Script that evaluates movie script parser')
    parser.add_argument("-d", "--dir", help="Path to directory containing parsed output tags", required=True)
    parser.add_argument("-m", "--mode", help="Choose mode to run in: e (full evaluation), i (inspect confusions)", required=True, default='e')
    parser.add_argument("-n", "--topn", help="Choose number of confusions to inspect (less than 25)", type=int, default=5)
    args = parser.parse_args()
    if args.mode == 'i' and args.topn > 25: raise AssertionError("Cannot inspect more than 25 confusions")
    return os.path.abspath(args.dir), args.mode, args.topn


# THIS EXTRACTS GROUND TRUTH AND PREDICTED LABELS
def get_labels():
    mica_labels = []
    for movie, beg, end in zip(movies, begs, ends):
        output_tag_path = parser_noindent_dir + '/' + movie + '_tags.txt'
        labels = np.genfromtxt(output_tag_path, dtype=str, delimiter='\n')
        labels = ''.join(labels).replace('0', ' ')
        if movie == 'grosse_pointe_blank':
            labels = labels[beg - 2: end - 1]
        else:
            labels = labels[beg - 1: end]
        
        mica_labels.append(labels)
    
    gold_labels = calc_gold_annotations()
    return gold_labels, mica_labels


# WRITE GROUND TRUTH AND PREDICTED LABELS TO FILE FOR COMPARISON
def write_labels(orig_labels, pred_labels):
    for mov_ind in range(len(orig_labels)):
        # READ MOVIE SEGMENT
        fid = open('data/files/' + movies[mov_ind] + '.csv', 'r')
        mov_file = fid.read().splitlines()
        fid.close()
        # APPEND LABELS
        fid = open(res_dir + 'inspect/' + movies[mov_ind] + '.csv', 'w')
        _ = fid.write(mov_file[0] + ',GroundTruth,Predicted\n')
        _ = fid.write(mov_file[1] + ',G,P\n')
        for line_ind in range(len(orig_labels[mov_ind])):
            gt_str = orig_labels[mov_ind][line_ind]
            pred_str = pred_labels[mov_ind][line_ind]
            _ = fid.write(mov_file[line_ind + 2] + ',' + gt_str + ',' + pred_str + '\n')
        
        fid.close()


# THIS PRE-PROCESSES LABELS TO REMOVE ANNOTATOR MISMATCH AND CONCATENATES INTO SINGLE SEQUENCE
def process_labels(orig_labels, pred_labels):
    M = "".join(pred_labels)
    G = "".join(orig_labels)
    M = np.array(list(M))
    G = np.array(list(G))
    mask = (G != 'X')
    G = G[mask]
    M = M[mask]
    return G, M


# print precision, recall and F1 scores for mica labels against gold labels for dialogue (class = D), 
# character (class = C) and scene boundaries (class = S)
def evaluate_mica(orig_labels, pred_labels):
    for class_id in eval_list:
        prec_val, rec_val, f1_val = calc_score(orig_labels, pred_labels, class_id)
        print(class_id + ": prec = {:.3f} rec = {:.3f} f1 = {:.3f}".format(prec_val, rec_val, f1_val))


# WRITE CONFUSION MATRIX
def write_conmat(con_mat, con_class, write_path):
    fid = open(write_path + 'confusion_matrix.csv', 'w')
    _ = fid.write(','.join([' '] + [x for x in con_class]) + '\n')
    for ind in range(con_mat.shape[0]):
        con_norm = (con_mat[ind, :] / sum(con_mat[ind, :])) * 100
        _ = fid.write(','.join([con_class[ind]] + ["%.2f"%x for x in con_norm]) + '\n')
    
    fid.close()


# COMPUTE CONFUSION MATRIX
def get_conmat(orig_labels, pred_labels):
    class_labels, class_counts = np.unique(orig_labels, return_counts=True)
    conmat = confusion_matrix(orig_labels, pred_labels, labels=class_labels)
    return conmat, class_labels


# COMPUTE CONFUSION MATRIX AND WRITE TO FILE
def get_top_conf(con_mat, con_class, top_thresh):
    conf_map = {}
    for iter1 in range(con_mat.shape[0]):
        true_class = con_class[iter1]
        if true_class in eval_list:
            for iter2 in range(con_mat.shape[1]):
                confused_class = con_class[iter2]
                if iter1 != iter2 and confused_class in eval_list:
                    rec_val = con_mat[iter1, iter2] / sum(con_mat[iter1, :])
                    conf_map[true_class + '_' + confused_class] = rec_val
    
    top_ind = np.argsort(list(conf_map.values()), axis=0)[-(top_thresh): ]
    conf_set = {list(conf_map.keys())[x]: list(conf_map.values())[x] for x in top_ind[: : -1]}
    return conf_set


# FIND RECALL VALUE FOR SPECIFIC CONFUSION
def find_conf_val(con_mat, con_class, con_type):
    lab_true, lab_pred = con_type.split('_')
    if lab_true in con_class and lab_pred in con_class:
        con_val = con_mat[con_class.index(lab_true), con_class.index(lab_pred)]
    else:
        con_val = 0
    
    return con_val


# GET RECALL VALUES FOR TOP CONFUSIONS FROM ALL MOVIES
def get_conf(conf_list):
    all_conf = {}
    for con_type in list(conf_list):
        conf_vec = np.zeros((len(movies), 1), dtype=float)
        for mov_ind in range(len(movies)):
            mov_gt, mov_pred = process_labels(gt_orig[mov_ind], pred_orig[mov_ind])
            con_mat, con_class = get_conmat(mov_gt, mov_pred)
            conf_vec[mov_ind] = find_conf_val(con_mat, list(con_class), con_type)
        
        all_conf[con_type] = conf_vec
    
    return all_conf


# MAIN
if __name__ == "__main__":
    # DEFINE
    eval_list = ['D', 'C', 'S', 'T', 'N', 'E']
    res_dir = 'results/'
    # READ FILES
    parser_noindent_dir, parser_mode, top_conf = read_args()
    movies, begs, ends = read_annotation_movies()
    # GET MAIN RESULTS
    os.system('mkdir -p ' + res_dir)
    os.system('mkdir -p ' + res_dir + 'inspect/')
    gt_orig, pred_orig = get_labels()
    write_labels(gt_orig, pred_orig)
    gt_proc, pred_proc = process_labels(gt_orig, pred_orig)
    if parser_mode == 'e':
        # RUN OVERALL EVALUATION
        evaluate_mica(gt_proc, pred_proc)
    elif parser_mode == 'i':
        # FIND FREQUENTLY CONFUSED CLASSES
        conf_mat, gt_class = get_conmat(gt_proc, pred_proc)
        write_conmat(conf_mat, gt_class, res_dir)
        conf_rec = get_top_conf(conf_mat, gt_class, top_conf)
        print('\nTop ' + str(top_conf) + ' confusions:')
        for x in conf_rec:
            print(x + ': ' + str(conf_rec[x]))
        
        # FOR EACH CONFUSION, SHOW TOP CONFUSED MOVIES
        print('\nTop ' + str(top_conf) + ' confused movies')
        mov_conf = get_conf(conf_rec.keys())
        for conf_id in mov_conf.keys():
            print('\n' + conf_id)
            top_mov = list([x[0] for x in np.argsort(mov_conf[conf_id], axis=0)[-(top_conf): ]])
            for x in top_mov[: : -1]:
                print(movies[x] + ': ' + str(mov_conf[conf_id][x][0]))