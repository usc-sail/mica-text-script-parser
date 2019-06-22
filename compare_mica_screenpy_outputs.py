import os
import json
import numpy as np
from pprint import pprint
from shutil import copyfile
from stats import get_stats_report
from count_common_files import count_common_files

mica_parser_output_dir = "../mica-scripts/parsed_scripts_with_context/"
scpy_parser_output_dir = "../screenpy/ParserOutput/"


def write_utterances_and_scripts(scpy_filepath, mica_filepath):
    movie = os.path.basename(scpy_filepath).replace(".json", "")
    scpy_utterances = []
    mica_utterances = []

    print(f"extracting screenpy and mica utterances for {movie} for comparison...")

    scpy_parser_output = json.load(open(scpy_filepath))
    for mseg in scpy_parser_output:
        for seg in mseg:
            if seg["head_type"] == "speaker/title":
                character = seg["head_text"]["speaker/title"].strip()
                utterance = seg["text"].strip()
                scpy_utterances.append((character, utterance))
    
    mica_parser_output = open(mica_filepath).read()
    for line in mica_parser_output.split("\n"):
        if not line.startswith("#####"):
            character, utterance = line.split("=>")
            character = character.strip()
            utterance = utterance.strip()
            mica_utterances.append((character, utterance))

    directory = os.path.join("compare_outputs", movie)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    
    scpy_utterance_filepath = os.path.join(directory, "screenpy_utterances.txt")
    with open(scpy_utterance_filepath, "w") as fw:
        for character, utterance in scpy_utterances:
            fw.write(f"{character:30s} => {utterance}\n")

    mica_utterance_filepath = os.path.join(directory, "mica_utterances.txt")
    with open(mica_utterance_filepath, "w") as fw:
        for character, utterance in mica_utterances:
            fw.write(f"{character:30s} => {utterance}\n")

    scpy_script_filepath_src = scpy_filepath.replace("ParserOutput", "imsdb_raw_nov_2015").replace(".json", ".txt")
    mica_script_filepath_src = mica_filepath.replace("parsed_scripts_with_context","scripts_txt")
    scpy_script_filepath_dst = os.path.join(directory, "screenpy_script.txt")
    mica_script_filepath_dst = os.path.join(directory, "mica_script.txt")

    copyfile(scpy_script_filepath_src, scpy_script_filepath_dst)
    copyfile(mica_script_filepath_src, mica_script_filepath_dst)


def compare_mica_screenpy_outputs():
    np.random.seed(0)

    scpy_filename_to_genre, mica_hash_dict, mica_empty_filenames, common_files_info = count_common_files()
    common_parser_files_info = []

    for i, (scpy_filename, hash_key) in enumerate(common_files_info):
        genres = scpy_filename_to_genre[scpy_filename]
        mica_filenames = mica_hash_dict[hash_key]

        scpy_filepaths = [os.path.join(scpy_parser_output_dir, genre, scpy_filename.replace(".txt", ".json")) for genre in genres]
        nonempty_scpy_filepaths = [fp for fp in scpy_filepaths if json.load(open(fp))]
        
        mica_filepaths = [os.path.join(mica_parser_output_dir, f) for f in mica_filenames]
        found_mica_filepaths = [fp for fp in mica_filepaths if os.path.exists(fp)]

        if nonempty_scpy_filepaths and found_mica_filepaths:
            common_parser_files_info.append((nonempty_scpy_filepaths, found_mica_filepaths))

    print(f"#files for which parsed output is in both {mica_parser_output_dir} and {scpy_parser_output_dir} = {len(common_parser_files_info)}")
    print()

    indices = np.arange(len(common_parser_files_info))
    # random_indices = np.random.choice(indices, size=5, replace=False)
    # for i in random_indices:
    #     scpy_filepath, mica_filepaths = common_parser_files_info[i]
    #     write_utterances_and_scripts(scpy_filepath, mica_filepaths[0])
    # print()

    diff_n_utterances = []
    for scpy_filepaths, mica_filepaths in common_parser_files_info:
        scpy_parser_output = json.load(open(scpy_filepaths[0]))
        n_scpy_utterances = sum(1 for mseg in scpy_parser_output for seg in mseg if seg["head_type"] == "speaker/title")

        mica_parser_output = open(mica_filepaths[0]).read()
        n_mica_utterances = sum(1 for line in mica_parser_output.split("\n") if not line.startswith("###"))

        diff_n_utterances.append(np.abs(n_scpy_utterances - n_mica_utterances))
    print(get_stats_report("DIFFERENCE in #UTTERANCES PARSED BETN screenpy AND mica", diff_n_utterances, bins = np.arange(start=0, stop=2000, step=100)))

    diff_n_utterances = np.array(diff_n_utterances)
    indices = np.argsort(-diff_n_utterances)
    selected_indices = indices[:5]
    for i in selected_indices:
        scpy_filepaths, mica_filepaths = common_parser_files_info[i]
        write_utterances_and_scripts(scpy_filepaths[0], mica_filepaths[0])
    print()

if __name__ == "__main__":
    compare_mica_screenpy_outputs()
