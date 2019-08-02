# author - Sabyasachee

import numpy as np
import krippendorff
from sklearn.metrics import cohen_kappa_score
from utils import read_annotations, LABELS

def calc_annotator_agreement():
    # calculates the inter rater agreement in terms of cohen's kappa between pairs of annotators, and krippendorff's alpha among all three annotators, and prints them
    # the classes used for cohen's kappa are S, N, C, D, E and T
    # all classes are used for krippendorf's alpha
    annotations_A = read_annotations("data/annotations/Annotator 1.xlsx")
    annotations_B = read_annotations("data/annotations/Annotator 2.xlsx")
    annotations_C = read_annotations("data/annotations/Annotator 3.xlsx")

    A = "".join(annotations_A)
    B = "".join(annotations_B)
    C = "".join(annotations_C)

    A = np.array(list(A))
    B = np.array(list(B))
    C = np.array(list(C))

    kappa_AB = cohen_kappa_score(A, B, labels = ["S","N","C","D","E","T"])
    kappa_BC = cohen_kappa_score(B, C, labels = ["S","N","C","D","E","T"])
    kappa_AC = cohen_kappa_score(A, C, labels = ["S","N","C","D","E","T"])

    print("Inter-rater agreement (Cohen Kappa)")
    print("\t\tMing - Saby       = {:.3f}".format(kappa_AB))
    print("\t\tSaby - Tian       = {:.3f}".format(kappa_BC))
    print("\t\tTian - Ming       = {:.3f}".format(kappa_AC))

    a = np.array([LABELS.index(x) for x in A])
    b = np.array([LABELS.index(x) for x in B])
    c = np.array([LABELS.index(x) for x in C])

    data = np.vstack((a, b, c))
    alpha = krippendorff.alpha(data, level_of_measurement="nominal")
    print("Inter-rater agreement (Krippendorf's alpha)")
    print("\t\tMing, Saby, Tian  = {:.3f}".format(alpha))

if __name__ == "__main__":
    calc_annotator_agreement()