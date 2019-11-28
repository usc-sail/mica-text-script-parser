#!/usr/bin/env python

import sys
import os
from parse_scripts import *
from fetch_scripts import *
from extract_scripts import *
from distutils.util import strtobool
from settings import DATA_FOLDER

#leave this variable blank if there are no noisy scripts
noisy_movies_path='noisy_movies_list.txt'

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

html_dir = os.path.join(DATA_FOLDER, "scripts_html")
pdf_dir = os.path.join(DATA_FOLDER, "scripts_pdf")
text_dir = os.path.join(DATA_FOLDER, "scripts_text")
out_dir = os.path.join(DATA_FOLDER, "scripts_parsed")
info_path = os.path.join(DATA_FOLDER, "info.csv")

if not os.path.exists(html_dir): os.makedirs(html_dir)
if not os.path.exists(pdf_dir): os.makedirs(pdf_dir)
if not os.path.exists(text_dir): os.makedirs(text_dir)
if not os.path.exists(out_dir): os.makedirs(out_dir)

if len(sys.argv)==1:
    fetch_and_parse_first = True
else:
    fetch_and_parse_first = strtobool(sys.argv[1])
    
if fetch_and_parse_first:
    #Get imsdb scripts
    f=fetch_scripts('imsdb', html_dir, pdf_dir, text_dir, info_path)
    f.fetch_data()

    #Get dailyscript scripts
    f=fetch_scripts('dailyscript', html_dir, pdf_dir, text_dir, info_path)
    f.fetch_data()

    #Extract text scripts from fetched html files
    e=extract_scripts(html_dir, pdf_dir, text_dir, noisy_movies_path, info_path)
    e.extract_scripts()

files=os.listdir(text_dir)

for file in files:
    filepath=os.path.join(text_dir, file)
    outpath=os.path.join(out_dir, file)
    p=script_parser(filepath, outpath)
    p.process()
    print("Done parsing {0}".format(file))
