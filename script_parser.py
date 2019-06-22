from parse_scripts import script_parser
from screenpy import screenpile
import json

# parser = script_parser("examples/2012_mica.txt", "examples/2012_mica_out.txt")
# parser.process()

screenplay = open("compare_outputs/margaret/screenpy_utterances.txt").read()
parse_output = screenpile.annotate(screenplay)
json.dump(parse_output, open("margaret.new.json", "w"), indent=4)
