#!/usr/bin/env python

import sys
from parse_scripts import *
from fetch_scripts import *
from extract_scripts import *
from distutils.util import strtobool

html_dir = '../Data/scripts_html'
pdf_dir = '../Data/scripts_pdf'
text_dir = '../Data/scripts_txt'
out_dir = '../Data/utterances_with_charnames'

if len(sys.argv)==1:
    fetch_and_parse_first = True
else:
    fetch_and_parse_first = strtobool(sys.argv[1])
    
if fetch_and_parse_first:
    #Get imsdb scripts
    f=fetch_scripts('imsdb', html_dir, pdf_dir, text_dir)
    f.fetch_data()

    #Get dailyscript scripts
    f=fetch_scripts('dailyscript', html_dir, pdf_dir, text_dir)
    f.fetch_data()

    #Extract text scripts from fetched html files
    e=extract_scripts(html_dir, pdf_dir, text_dir)
    e.extract_scripts()

files=os.listdir(text_dir)

for file in files:
    filepath=os.path.join(text_dir, file)
    outpath=os.path.join(out_dir, file)
    p=script_parser(filepath, outpath)
    p.process()
    print("Done parsing {0}".format(file))
