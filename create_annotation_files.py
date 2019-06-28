import os
import re
import numpy as np
from count_indent_distribution import count_indent_distribution
from prepare_for_annotation import prepare_for_annotation


def create_annotation_files():
    np.random.seed(0)

    mica_scripts_dir = "../mica-scripts/scripts_txt/"
    n_indents_to_filenames = count_indent_distribution()
    n_indents_range_n_files = [(1,1,5), (2,2,5), (3,3,5), (4,4,5), (5,5,2), (6,6,2), (7,7,2), (8,8,2), (9,9,2),(10,20,5), (20,60,5)]
    n_lines = 250

    for lo_n_indents, hi_n_indents, n_files in n_indents_range_n_files:
        filenames = []
        for n_indents in range(lo_n_indents, hi_n_indents + 1):
            if n_indents in n_indents_to_filenames:
                filenames.extend(n_indents_to_filenames[n_indents])
        
        filenames = np.array(filenames)
        filenames = np.random.permutation(filenames)
        good_filename_start_end_indices = []

        for filename in filenames:
            any_good_start = False
            
            filepath = os.path.join(mica_scripts_dir, filename)
            screenplay = open(filepath, "r").read().split("\n")
            starts = np.arange(len(screenplay) - n_lines)
            starts = np.random.permutation(starts)

            for start in starts:
                end = start
                unique_indents = set()
                n_non_empty_lines = 0

                while end < len(screenplay) and n_non_empty_lines != n_lines:
                    if screenplay[end].strip():
                        n_non_empty_lines += 1
                        indent = re.match(r"^[\s]*", screenplay[end]).span()[1]
                        unique_indents.add(indent)
                    end += 1

                if len(unique_indents) >= lo_n_indents:
                    any_good_start = True
                    break

            if any_good_start:
                good_filename_start_end_indices.append((filename, start, end))
                if len(good_filename_start_end_indices) == n_files:
                    break

        print(f"N_INDENT_RANGE = [{lo_n_indents:2d},{hi_n_indents:2d}]")
        for filename, start, end in good_filename_start_end_indices:
            print(f"\t\t{filename:30s}  [{start:5d}, {end:5d}]")
            script_filepath = os.path.join(mica_scripts_dir, filename)
            annotation_filepath = os.path.join("annotation/", filename.replace(".txt", ".csv"))
            prepare_for_annotation(script_filepath, annotation_filepath, start, end)
        print()

if __name__ == "__main__":
    create_annotation_files()
