import os
from check_duplicates import find_duplicates, hash_content

def count_common_files():
    mica_scripts_dir = "../mica-scripts/scripts_txt/"
    scpy_scripts_dir = "../screenpy/imsdb_raw_nov_2015/"
    mica_hash_dict, mica_empty_filenames = find_duplicates(mica_scripts_dir, ext="txt")
    print()

    genres = [d for d in os.listdir(scpy_scripts_dir) if os.path.isdir(os.path.join(scpy_scripts_dir, d))]
    filename_to_genres = {}
    scpy_hash_dict = {}
    scpy_empty_filenames = []

    for g in genres:
        for filename in os.listdir(os.path.join(scpy_scripts_dir, g)):
            if filename.endswith(".txt"):
                if filename not in filename_to_genres:
                    filename_to_genres[filename] = []
                filename_to_genres[filename].append(g)


    for filename, genres in filename_to_genres.items():
        content = open(os.path.join(scpy_scripts_dir, genres[0], filename)).read()
        if len(content) < 50:
            scpy_empty_filenames.append(filename)
        else:
            hash_key = hash_content(content)
            if hash_key not in scpy_hash_dict:
                scpy_hash_dict[hash_key] = []
            scpy_hash_dict[hash_key].append(filename)

    print(f"#files in {scpy_scripts_dir} directories = {len(filename_to_genres)}")
    print(f"empty files in {scpy_scripts_dir} directories = {len(scpy_empty_filenames)}")
    print(f"#unique files in {scpy_scripts_dir} directories = {len(scpy_hash_dict)}")
    print()

    common_files = []
    for scpy_filename in filename_to_genres.keys():
        match = False
        for hash_key, mica_files in mica_hash_dict.items():
            for mica_file in mica_files:
                mica_file = mica_file.replace("_","").lower().strip()
                if mica_file == scpy_filename:
                    match = True
                    break
            if match:
                break
        if match:
            common_files.append((scpy_filename, hash_key))
    print(f"#common files between {mica_scripts_dir} and {scpy_scripts_dir} = {len(common_files)} (matching by filename)")
    print()

    print(f"{scpy_scripts_dir} files not present in {mica_scripts_dir}")
    scpy_common_files = set([f for f, _ in common_files])
    scpy_only_files = list(set(list(filename_to_genres.keys())).difference(scpy_common_files))
    scpy_only_files.sort()
    for f in scpy_only_files:
        print(f"\t{f}")
    print()

    return filename_to_genres, mica_hash_dict, mica_empty_filenames, common_files

if __name__ == "__main__":
    count_common_files()