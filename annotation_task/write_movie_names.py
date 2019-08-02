# author - Sabyasachee

import os
from check_duplicates import find_duplicates

def write_movie_names():
    # write list of unique non empty files in files.txt
    # get list of unique non empty files from parsed_scripts_with_context directory
    # check if file is present in scripts_txt

    mica_parsed_scripts_dir = "../../mica-scripts/parsed_scripts_with_context/"
    mica_scripts_dir = "../../mica-scripts/scripts_txt/"

    hash_dict, _ = find_duplicates(mica_parsed_scripts_dir, ext = "txt")
    files = []

    for _, filenames in hash_dict.items():
        filenames.sort()
        
        for filename in filenames:
            filepath = os.path.join(mica_scripts_dir, filename)
            if os.path.exists(filepath):
                content = open(filepath).read().replace(" ","").replace("\t","").strip().lower()
                if content and content != "scriptremoved":
                    files.append(filename)                    
                    break
    
    print(f"{len(files)} files available in {mica_scripts_dir}")
    with open("data/movies.txt", "w") as fw:
        files.sort()
        for filename in files:
            filename = filename.replace(".txt", "")
            fw.write(f"{filename}\n")

if __name__ == "__main__":
    write_movie_names()