from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import sys
import re
import PyPDF2
import pandas as pd

__detailedlog__ = True


class extract_scripts:
    def __init__(self,html_dir,pdf_dir,text_dir,noisy_movies_path, info_path):
        self.html_dir=html_dir
        self.pdf_dir=pdf_dir
        self.text_dir=text_dir
        self.noisy_movies_path=noisy_movies_path
        self.info_path=info_path

    def extract_from_html(self):
        if __detailedlog__:
            print("Extracting scripts from fetched html files...")

        if self.noisy_movies_path != None:
            inptr=open(self.noisy_movies_path)
            noisy_movies_list=[x.strip() for x in inptr.readlines()]
        else:
            noisy_movies_list=[]

        files_list = os.listdir(self.html_dir)

        info_df = pd.read_csv(self.info_path, index_col = 0)
        
        for file in files_list:
            if not file.endswith('html'):
                continue

            file_name = os.path.join(self.html_dir, file)
            out_file_name = os.path.join(self.text_dir, file.replace(".html", ".txt"))

            in_ptr = open(file_name)
            soup = BeautifulSoup(in_ptr, 'html.parser')
            pre_elements_list = soup.find_all('pre')
       
            file = info_df[info_df["file"] == file_name]["movie"].item()

            if len(pre_elements_list)==0:
                print("No pre elements in {0},".format(file), 
                    "skipping this file for now.",
                    "Maybe add them manually to enclose the script?")
                continue

            #ignore some files for now; they need to be manually cleaned
            if file in noisy_movies_list:
                continue

            largest_ind=0
            if len(pre_elements_list)>1:
                for iter in range(1,len(pre_elements_list)):
                    if len(pre_elements_list[iter])>len(pre_elements_list[largest_ind]):
                        largest_ind=iter
            screenplay = pre_elements_list[largest_ind].get_text().encode('ascii', 'ignore').decode('utf-8', 'ignore')

            #cleanup files before processing
            if file == 'evil_dead' or \
                file == 'chasing_sleep' or \
                file == 'clueless' or \
                file == 'incredibles_the' or \
                file == 'war_of_the_worlds' or \
                file == 'land_of_the_dead':
                screenplay = screenplay.replace('\n\n', '\n')

            if file == 'rescuers_down_under_the':
                screenplay = screenplay.replace('scene:', 'scene')

            if file == 'mulan' or \
                file == 'legend' or \
                file == 'little_mermaid' or \
                file == 'ninth_gate_the' or \
                file == 'rescuers_down_under_the' or \
                file == 'dawn_of_the_dead' or \
                file == 'star_wars_the_phantom_menace':
                screenplay = screenplay.replace(':', '\n')

            out_ptr = open(out_file_name, 'w')
            out_ptr.write(screenplay)
            out_ptr.close()
        
            if __detailedlog__:
                print("Extracted text for: {0}".format(file))
 
        print("Done extracting text from html scripts\n\n\n")

    def extract_from_pdf(self):
        if __detailedlog__:
            print("Extracting scripts from fetched pdf files...")

        files_list = os.listdir(self.pdf_dir)
        info_df = pd.read_csv(self.info_path, index_col = 0)

        for file in files_list:
            if not file.endswith('pdf'):
                continue

            file_name = os.path.join(self.pdf_dir, file)
            out_file_name = os.path.join(self.text_dir, file.replace(".pdf", ".txt"))
            file = info_df[info_df["file"] == file_name]["movie"].item()

            try:
                inptr=open(file_name, 'rb')
                pdfreader=PyPDF2.PdfFileReader(inptr)

                pages=[]
                for page in range(pdfreader.getNumPages()):
                    cur_text=pdfreader.getPage(page).extractText()
                    cur_text=cur_text.encode('utf8','ignore')
                    cur_text=cur_text.decode('utf8','ignore')
                    pages.append(cur_text)
                inptr.close()
            except PyPDF2.utils.PdfReadError:
                continue
            except Exception as e:
                print("Exception: {0};".format(type(e).__name__),
                        "Arguments: {0}".format(e.args))
                continue

            outptr=open(out_file_name, 'w')
            outptr.write(' '.join(pages))
            outptr.close()
            

            if __detailedlog__:
                print("Extracted text for: {0}".format(file))

        print("Done extracting text from pdf scripts\n\n\n")

    def extract_scripts(self):
        self.extract_from_html()
        self.extract_from_pdf()
