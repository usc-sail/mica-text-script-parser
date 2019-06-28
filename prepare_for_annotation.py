import csv
import argparse

def prepare_for_annotation(script_filepath, annotation_filepath, i = 0, j = 500):
    lines = open(script_filepath).read().split("\n")
    writer = csv.writer(open(annotation_filepath, "w"))
    filler = ["" for _ in range(30)]

    writer.writerow(["","","Scene Boundary", "Scene Description/Direction", "Character", "Dialogue", "Dialogue Metadata", "Transition", "Metadata"])
    writer.writerow(["line","","S","N","C","D","E","T","M"])
    for line in lines[i: j + 1]:
        writer.writerow([line, "", "", "", "", "", "", "", ""])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="Prepare a screenplay text file for annotation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("inp", help = "input script filepath")
    parser.add_argument("out", help = "output annotation csv filepath")
    args = parser.parse_args()

    script_filepath = args.inp
    annotation_filepath = args.out

    prepare_for_annotation(script_filepath, annotation_filepath)
