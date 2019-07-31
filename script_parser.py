# author - Sabyasachee

import argparse
import re
import json

def script_parser(src, dst = None, algo = False, utter = False, write = True, verbose = False):
    # parse screenplay found at src filepath and save output at dst filepath
    # if algo is True, use screenpy parser, else use mica parser
    # if utter is True, print number of utterances parsed for top 5 characters
    # if write is true, write parser output to dst

    if algo:
        from screenpy.screenpile import annotate
        screenplay = open(src).read()
        parse_output = annotate(screenplay)
        json.dump(parse_output, open(dst, "w"), indent=4)
    else:
        from mica.parse_scripts import script_parser
        parser = script_parser(src, dst, write, verbose)
        label_sequence = parser.process()       

    if utter:
        character_to_utterances = {}
        total_n_utterances = 0
        parantheses_regex = re.compile(r"\([^)]*\)")

        if algo:
            for mseg in parse_output:
                for seg in mseg:
                    if seg["head_type"] == "speaker/title":
                        character = seg["head_text"]["speaker/title"]
                        utterance = seg["text"].strip()
                        character = re.sub(parantheses_regex, "", character).strip()

                        if character not in character_to_utterances:
                            character_to_utterances[character] = []
                        character_to_utterances[character].append(utterance)
                        total_n_utterances += 1

        else:
            with open(dst) as fr:
                for line in fr:
                    if not line.startswith("#####"):
                        character, utterance = line.split("=>")
                        character = re.sub(parantheses_regex, "", character).strip()
                        utterance = utterance.strip()

                        if character not in character_to_utterances:
                            character_to_utterances[character] = []
                        character_to_utterances[character].append(utterance)
                        total_n_utterances += 1
            
        
        character_n_utterances_tuples = [(character, len(utterances)) for character, utterances in character_to_utterances.items()]
        character_n_utterances_tuples = sorted(character_n_utterances_tuples, key = lambda x: x[1], reverse = True)
        for character, n_utterances in character_n_utterances_tuples[:5]:
            print(f"{character:20s} => {n_utterances:4d} turns")
        print(f"total {total_n_utterances} turns parsed")

    return label_sequence

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="mica screenplay parser", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", help = "filepath of screenplay text file")
    parser.add_argument("output", help = "filepath of parsed output")
    parser.add_argument("-a", action = "store_true", dest = "algo", default = False, help = "set to use screenpy parser; default to mica parser")
    parser.add_argument("-u", action = "store_true", dest = "utter", default = False, help = "set to print number of utterances parsed for top 5 characters and in total")
    parser.add_argument("-w", action = "store_true", dest = "write", default = False, help = "set to write to output filepath")
    parser.add_argument("-v", action = "store_true", dest = "verbose", default = False, help = "verbose")

    args = parser.parse_args()
    src = args.input
    dst = args.output
    algo = args.algo
    utter = args.utter
    write = args.write
    verbose = args.verbose

    script_parser(src, dst, algo, utter, write, verbose)