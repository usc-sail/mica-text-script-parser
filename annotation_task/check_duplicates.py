# author Sabyasachee

import os
import hashlib
import argparse

def hash_content(content):
    # hash content string and return hash key
    # remove all whitespaces and lowercase content string
    # use md5 hash algorithm to hash and return hash key

    content = content.strip().replace(" ", "").replace("\t", "").lower()
    hash_obj = hashlib.md5(content.encode())
    hash_key = hash_obj.hexdigest()
    return hash_key

def find_duplicates(directory, ext = None, verbose = False):
    # find empty and duplicate files in directory
    # returns tuple hash_dict, empty_filenames
    # hash_dict is dictionary of hash_key and list of files. files with the same hash key are duplicates of each other
    # empty_filenames is list of empty file names

    if ext:
        filenames = [f for f in os.listdir(directory) if f.endswith("." + ext)]
    else:
        filenames = os.listdir(directory)

    hash_dict = {}
    empty_filenames = []

    for filename in filenames:
        content = open(os.path.join(directory, filename)).read().strip()
        if not content or content == "Script Removed":
            empty_filenames.append(filename)
        else:
            hash_key = hash_content(content)
            if hash_key not in hash_dict:
                hash_dict[hash_key] = []
            hash_dict[hash_key].append(filename)

    print(f"#files in {directory} = {len(filenames)}")
    print(f"#empty files in {directory} = {len(empty_filenames)}")
    print(f"#non empty files in {directory} = {len(filenames) - len(empty_filenames)}")
    print(f"#non empty unique files in {directory} = {len(hash_dict)}")

    if verbose:
        print()
        print("duplicate sets =>")
        i = 0
        for _, filenames in hash_dict.items():
            if len(filenames) > 1:
                i += 1
                filenames.sort()
                print(f"{i:2d}. {filenames}")

    return hash_dict, empty_filenames

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="find duplicates in directory", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("directory", help = "directory to search in")
    parser.add_argument("-e", default = None, dest = "ext", help = "check only files with this extension")
    parser.add_argument("-v", action = "store_true", dest = "verbose", default = False, help = "set to print duplicates")
    args = parser.parse_args()

    directory = args.directory
    ext = args.ext
    verbose = args.verbose
    find_duplicates(directory, ext, verbose)