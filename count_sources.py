#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import sys
import re

__detailedlog__ = True

class fetch_scripts:
    def __init__(self, source, html_dir=None, pdf_dir=None, text_dir=None):
        if html_dir == None:
           self.html_dir='.'
        else:
           self.html_dir=html_dir

        if pdf_dir == None:
            self.pdf_dir='.'
        else:
            self.pdf_dir=pdf_dir

        if text_dir== None:
            self.text_dir='.'
        else:
            self.text_dir=text_dir

        self.source=source
        if self.source.lower() == 'imsdb':
            self.source_url_list=['http://www.imsdb.com/all%20scripts/']
        elif self.source.lower() == 'dailyscript':
            self.source_url_list=['http://www.dailyscript.com/movie.html',
            'http://www.dailyscript.com/movie_n-z.html']           
        self.html_counter=0
        self.pdf_counter=0
        self.total_fetched=0
        self.text_counter=0

    def print_fetch_stats(self):
        print("Done fetching scripts from {0}".format(self.source))
        print("{0} files downloaded;".format(self.total_fetched), 
            "of which {0} were html".format(self.html_counter), 
            "{0} were pdf and".format(self.pdf_counter),
            "{0} were text files".format(self.text_counter))

    def fetch_data(self):
        if __detailedlog__:
            print("Fetching data from {0}...".format(self.source))

        encountered_movies_list = []

        self.total_fetched = 0

        for source_url in self.source_url_list:
            response = urlopen(source_url)        
            soup = BeautifulSoup(response, 'html5lib')
            if self.source == 'imsdb':
                url_prefix='http://www.imsdb.com'
                identifier='/Movie Scripts/'
            elif self.source == 'dailyscript':
                url_prefix='http://www.dailyscript.com/'
                identifier='scripts/'
    
            urls_list = [x for x in soup.find_all('a') \
                if x.get('href').startswith(identifier)]
            self.total_fetched += len(urls_list)
            alphanum=re.compile(r'[^\w\.\& ]*')
     
            for cur_url in urls_list:
                try:
                    movie_name = cur_url.text
                    movie_response = urlopen(url_prefix + \
                        cur_url.get('href').replace(' ', '%20'))
                except Exception as e:
                    print("Fetch failed for movie {0}".format(movie_name))
                    print("Exception: {0};".format(type(e).__name__), 
                        "Arguments: {0}".format(e.args))
                    sys.exit()
  
                if self.source == 'imsdb': 
                    soup = BeautifulSoup(movie_response, 'html5lib')
                    tmp_urls_list = [x for x in soup.find_all('a') \
                        if x.get_text() == 'Read "'+movie_name+'" Script']
                    if len(tmp_urls_list) == 0:
                        continue
                    assert(len(tmp_urls_list) == 1)
                    cur_url=tmp_urls_list[0]
                    url_suffix=cur_url.get('href').replace(' ', '%20')
                    movie_response = urlopen(url_prefix + url_suffix)

                movie_name=alphanum.sub('', movie_name)
                movie_name=movie_name.lower()
                movie_name=movie_name.strip()
                movie_name=movie_name.replace(' ', '_')
                movie_name=movie_name.replace('&', 'and')

                if cur_url.get('href').lower().endswith('pdf'):
                    self.pdf_counter += 1
    
                elif cur_url.get('href').lower().endswith('html') or \
                    cur_url.get('href').lower().endswith('htm'):
                    self.html_counter += 1
 
                elif cur_url.get('href').lower().endswith('txt'):
                    self.text_counter += 1

                else:
                    print("Encountered unknown filetype: {0}".\
                        format(cur_url.get('href')))
                    continue

                encountered_movies_list.append(movie_name)

                if False:
                    print("Fetched movie: {0}".format(movie_name))
            
        self.print_fetch_stats()
