from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import sys
import re
import pickle
import pandas as pd
import uuid

__detailedlog__ = True

class fetch_scripts:
    def __init__(self, source, html_dir, pdf_dir, text_dir, info_path):
        self.source=source
        self.html_dir = html_dir
        self.pdf_dir = pdf_dir
        self.text_dir = text_dir
        self.info_path = info_path        
        
        if self.source.lower() == 'imsdb':
            self.source_url_list=['http://www.imsdb.com/all%20scripts/']
        elif self.source.lower() == 'dailyscript':
            self.source_url_list=['http://www.dailyscript.com/movie.html','http://www.dailyscript.com/movie_n-z.html']
        else:
            self.source_url_list=[]       
        
        self.html_counter=0
        self.pdf_counter=0
        self.text_counter=0

    def print_fetch_stats(self):
        print("Done fetching scripts from {0}".format(self.source))
        print("{} files downloaded: {} html + {} pdf + {} text".format(self.html_counter+self.pdf_counter+self.text_counter, self.html_counter, self.pdf_counter, self.text_counter))

    def fetch_data(self):
        info = {}
        n = 0
        
        if os.path.exists(self.info_path):
            info_df = pd.read_csv(self.info_path, index_col = 0)
            for _, row in info_df.iterrows():
                info[(row["source"], row["home_url"], row["movie_url"])] = (row["file"], row["movie"], row["imdb"])

        for source_url in self.source_url_list:
            response = urlopen(source_url)        
            soup = BeautifulSoup(response, 'html5lib')

            if self.source == 'imsdb':
                url_prefix='http://www.imsdb.com'
                identifier='/Movie Scripts/'
            elif self.source == 'dailyscript':
                url_prefix='http://www.dailyscript.com/'
                identifier='scripts/'
    
            if self.source == "imsdb":
                urls_list = [x for x in soup.find_all('a') if x.get('href').startswith(identifier)]
                imdb_list = [None for _ in range(len(urls_list))]
            else:
                table = soup.find_all("table")[2]
                p_elements = table.find("ul").find_all("p")
                urls_list, imdb_list = [], []
                for p_element in p_elements:
                    a_elements = p_element.find_all("a")
                    url, imdb = None, None
                    for a_element in a_elements:
                        if a_element.get("href").startswith(identifier):
                            url = a_element
                        elif a_element.text == "imdb" and "imdb.com" in a_element.get("href"):
                            imdb = a_element.get("href")
                    if url:
                        urls_list.append(url)
                        imdb_list.append(imdb)
            alphanum=re.compile(r'[^\w\.\& ]*')
     
            for cur_url, imdb in zip(urls_list, imdb_list):

                movie_name = cur_url.text
                movie_url = url_prefix + cur_url.get('href').replace(' ', '%20')
                home_url = movie_url

                if (self.source, home_url, movie_url) in info:
                    print("{}: {} - {} already fetched".format(self.source, home_url, movie_url))
                    continue

                try:
                    movie_response = urlopen(movie_url)
                except Exception as e:
                    print("Fetch failed for movie {0}".format(movie_name))
                    print("Exception: {0};".format(type(e).__name__), 
                        "Arguments: {0}".format(e.args))
                    continue
                
                if self.source == 'imsdb':
                    soup = BeautifulSoup(movie_response, 'html5lib')
                    tmp_urls_list = [x for x in soup.find_all('a') if x.get_text() == 'Read "'+movie_name+'" Script']
                    if len(tmp_urls_list) == 0:
                        continue
                    assert(len(tmp_urls_list) == 1)
                    cur_url=tmp_urls_list[0]
                    url_suffix=cur_url.get('href').replace(' ', '%20')
                    home_url = movie_url
                    movie_url = url_prefix + url_suffix
                    
                    if (self.source, home_url, movie_url) in info:
                        print("{}: {} - {} already fetched".format(self.source, home_url, movie_url))
                        continue

                    try:
                        movie_response = urlopen(movie_url)
                    except Exception as e:
                        print("IMSDB Fetch failed for movie {}".format(movie_name))
                        print("Exception: {0};".format(type(e).__name__), "Arguments: {0}".format(e.args))
                        continue
                
                movie_name=alphanum.sub('', movie_name)
                movie_name=movie_name.lower()
                movie_name=movie_name.strip()
                movie_name=movie_name.replace(' ', '_')
                movie_name=movie_name.replace('&', 'and')

                if cur_url.get('href').lower().endswith('pdf'):
                    file_name = os.path.join(self.pdf_dir, "{}.pdf".format(uuid.uuid4().hex))
                    out_ptr = open(file_name, 'wb')
                    
                    print("{}\nSOURCE = {}\nHOME   = {}\nURL    = {}\nFILE   = {}\nMOVIE  = {}\nIMDB   = {}".format(n+1,self.source, home_url, movie_url, file_name, movie_name, imdb))
                    info[(self.source, home_url, movie_url)] = (file_name, movie_name, imdb)
                    
                    out_ptr.write(movie_response.read())
                    out_ptr.close()
                    self.pdf_counter += 1
                    n += 1
    
                elif cur_url.get('href').lower().endswith('html') or cur_url.get('href').lower().endswith('htm'):
                    file_name = os.path.join(self.html_dir, "{}.html".format(uuid.uuid4().hex))
                    fetched_text=movie_response.read().decode('utf8', 'ignore')    
                    #cleanup fetched html using the html5lib parser
                    soup=BeautifulSoup(fetched_text, 'html5lib')
                    out_ptr = open(file_name, 'w')
                    
                    print("{}\nSOURCE = {}\nHOME   = {}\nURL    = {}\nFILE   = {}\nMOVIE  = {}\nIMDB   = {}".format(n+1,self.source, home_url, movie_url, file_name, movie_name, imdb))
                    info[(self.source, home_url, movie_url)] = (file_name, movie_name, imdb)
                    
                    out_ptr.write(soup.decode())
                    out_ptr.close()
                    self.html_counter += 1
                    n += 1     
    
                elif cur_url.get('href').lower().endswith('txt'):
                    file_name = os.path.join(self.text_dir, "{}.txt".format(uuid.uuid4().hex))
                    out_ptr = open(file_name, 'w')

                    print("{}\nSOURCE = {}\nHOME   = {}\nURL    = {}\nFILE   = {}\nMOVIE  = {}\nIMDB   = {}".format(n+1,self.source, home_url, movie_url, file_name, movie_name, imdb))
                    info[(self.source, home_url, movie_url)] = (file_name, movie_name, imdb)

                    file_contents=movie_response.read().decode('utf8', 'ignore')
                    out_ptr.write(file_contents)
                    out_ptr.close()
                    self.text_counter += 1
                    n+=1

                else:
                    print("Encountered unknown filetype: {0}".format(cur_url.get('href')))
                    continue
                
                print("\n")

        self.print_fetch_stats()
        print("\n\n")

        sources, home_urls, movie_urls, filepaths, movies, imdbs = [], [], [], [], [], []
        for (source, home_url, movie_url), (filepath, movie, imdb) in info.items():
            sources.append(source)
            home_urls.append(home_url)
            movie_urls.append(movie_url)
            filepaths.append(filepath)
            movies.append(movie)
            imdbs.append(imdb)
        info_df = pd.DataFrame.from_dict({"source": sources, "home_url": home_urls, "movie_url": movie_urls, "file": filepaths, "movie": movies, "imdb": imdbs})
        info_df.index.name = "id"
        info_df.to_csv(self.info_path)