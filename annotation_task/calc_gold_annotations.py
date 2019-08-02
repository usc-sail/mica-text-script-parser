# author - Sabyasachee

from utils import read_annotations
from statistics import mode

def calc_gold_annotations():
    # calculate gold annotations from the annotations of all three annotators
    # gold annotations are calculated by taking the majority
    # in case of no majority, put X in the gold annotation sequence
    # 
    # return the gold annotations, it is a list of strings, each string the annotation sequence of the annotation movie

    annotations_A = read_annotations("data/annotations/Annotator 1.xlsx")
    annotations_B = read_annotations("data/annotations/Annotator 2.xlsx")
    annotations_C = read_annotations("data/annotations/Annotator 3.xlsx")
    gold_annotations = []
    n_errors = 0

    for annotation_A, annotation_B, annotation_C in zip(annotations_A, annotations_B, annotations_C):
        gold_annotation = ""
        for x, y, z in zip(annotation_A, annotation_B, annotation_C):
            try:
                w = mode([x, y, z])
            except Exception:
                w = "X"
                n_errors += 1
            gold_annotation += w
        gold_annotations.append(gold_annotation)

    print("{} errors (no majority)...replaced with 'X'".format(n_errors))
    return gold_annotations

if __name__ == "__main__":
    calc_gold_annotations()