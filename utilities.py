#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import sys

__detailedlog__=True

class fetch_imsdb_scripts_in_html:
    def __init__(self, out_dir=None):
        if out_dir == None:
            self.out_dir='.'
        else:
            self.out_dir=out_dir

        self.imsdb_url='http://www.imsdb.com/all%20scripts/'

        self.success_counter=0
        self.pdf_counter=0
        self.total_fetched=0

    def print_fetch_stats(self):
        print("Done fetching scripts in html")
        print("{0} of {1} downloaded successfully. {2} were pdf files".format(self.success_counter, self.total_fetched, self.pdf_counter))

    def fetch_data(self):
        response = urlopen(self.imsdb_url)        
        soup = BeautifulSoup(response, 'html5lib')
        url_list = [x for x in soup.find_all('a') if x.get('href').startswith('/Movie Scripts/')]
        self.total_fetched=len(url_list)
   
        if __detailedlog__:
            print("Fetching data from imsdb...")     
        for cur_url in url_list:
            try:
                movie_name = cur_url.text
                movie_response = urlopen('http://www.imsdb.com' + cur_url.get('href').replace(' ', '%20'))
                movie_soup = BeautifulSoup(movie_response, 'html5lib')
        
                cur_url_list = [x for x in movie_soup.find_all('a') if x.get_text() == 'Read "'+movie_name+'" Script']
       
                if __detailedlog__: 
                    assert(len(cur_url_list) == 1)
       
                # Skip pdf files for now; TODO: parse pdf 
                if cur_url_list[0].get('href').endswith('pdf'):
                    self.pdf_counter += 1
                    continue
        
                out_ptr = open(os.path.join(outDir, movie_name.lower().replace(' ','_')+'.html'), 'w')
                script_response = urlopen('http://www.imsdb.com' + cur_url_list[0].get('href').replace(' ', '%20'))
                out_ptr.write(script_response.read().decode('utf-8', 'ignore'))
                out_ptr.close()
        
                if __detailedlog__:
                    print("Fetched movie: " + cur_url.get_text())
        
                self.success_counter += 1
        
            except Exception as e:
                print("Fetch failed for movie "+movie_name)
                print("Exception: {0}; Arguments: {1}".format(type(e).__name__, e.args))

        self.print_fetch_stats()

class extract_text_from_html:
    def __init__(self,html_dir,out_dir=None):
        self.html_dir=html_dir
        self.out_dir=out_dir

    def extract_text_data(self):
        if __detailedlog__:
            print("Extracting text from fetched html files...")
        for file in files_list:
            if not file.endswith('html'):
                continue
        
            in_ptr = open(os.path.join(html_dir, file))
            soup = BeautifulSoup(in_ptr, 'html5lib')
        
            pre_elements_list = soup.find_all('pre')
       
            if len(tmp_list)==0:
                print("No pre elements in file {0}; maybe add them manually enclosing the script?".format(file)) 
                continue

            largest_ind=0
            if len(pre_elements_list)>1:
                for iter in range(1,len(pre_elements_list)):
                    if len(pre_elements_list[iter])>len(pre_elements_list[largest_ind]):
                        largest_ind=iter
        
            out_ptr = open(os.path.join(out_dir, file.replace('html', 'txt')), 'w')
            out_ptr.write(pre_elements_list[largest_ind].get_text().encode('ascii', 'ignore').decode('ascii', 'ignore'))
            out_ptr.close()
        
            if __detailedlog__:
                print("Extracted text for: " + file)
        
        print("Done extracting scripts text")
