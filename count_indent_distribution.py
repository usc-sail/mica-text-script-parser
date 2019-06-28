import re
import os
import sys
import numpy as np
from collections import Counter
from check_duplicates import find_duplicates

def count_indent_distribution(verbose = False):
    np.random.seed(1)

    mica_parsed_scripts_dir = "../mica-scripts/parsed_scripts_with_context/"
    mica_scripts_dir = "../mica-scripts/scripts_txt/"

    hash_dict, empty_filenames = find_duplicates(mica_parsed_scripts_dir, ext = "txt")
    print("\n")
    n_indents_to_filenames = dict()

    for _, filenames in hash_dict.items():
        filepath = os.path.join(mica_scripts_dir, filenames[0])
        lines = open(filepath).read().split("\n")
        lines = [line for line in lines if line.strip()]
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
        
        # if n_indents == 0:
        #     print(filenames[0], indent_n_lines_tuples)
        #     print(cumul_n_lines, 0.95)
        #     sys.exit(0)

        if n_indents not in n_indents_to_filenames:
            n_indents_to_filenames[n_indents] = []
        n_indents_to_filenames[n_indents].append(filenames[0])

    print("#unique indent distribution for 95% of lines in screenplay\n")

    print(f"\t\t{'INDENTS':8s}\t{'FILES':8s}\t{'PERCENT':8s}\tFILENAMES")
    n_indents_list = sorted(list(n_indents_to_filenames.keys()))
    for n_indents in n_indents_list:
        n_files = len(n_indents_to_filenames[n_indents])
        percentage = 100*n_files/len(hash_dict)
        filenames = np.array(n_indents_to_filenames[n_indents])
        random_filenames = np.random.choice(filenames, size = min(5, filenames.size), replace = False)
        if verbose:
            print(f"\t\t{n_indents:8d}\t{n_files:8d}\t{percentage:8.2f}%\t{', '.join(random_filenames)}")
        else:
            print(f"\t\t{n_indents:8d}\t{n_files:8d}\t{percentage:8.2f}")
    print()

    return n_indents_to_filenames

if __name__ == "__main__":
    count_indent_distribution()
