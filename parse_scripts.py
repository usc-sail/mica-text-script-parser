#!/usr/bin/env python3

import sys
import os
import re
import string
from lxml import etree

class script_parser:
    def __init__(self, scriptfile, outfile):
        self.scriptfile=scriptfile
        self.outfile=outfile

    def remove_header_and_footer(self, script):
        lines=script.split('\n')

        punctuation=re.compile(r'['+string.punctuation+']')
        # keywords to detect script headers;
        # most script headers end with a date or the phrase "fade in"
        date=re.compile(r'''\bjanuary\b|
                \bfebruary\b|
                \bmarch\b|
                \bapril\b|
                \bmay\b|
                \bjune\b|
                \bjuly\b|
                \baugust\b|
                \bseptember\b|
                \boctober\b|
                \bnovember\b|
                \bdecember\b''', re.VERBOSE)
        keyword=re.compile(r'\bfade\b')

        header_found=False
        date_location=-1
        #remove header
        for i in range(len(lines))[:50]:
            line=lines[i].lower().strip()
            if date.search(line):
                date_location=i
            if keyword.match(line):
                header_found=True
                break

        if header_found == True:
            lines=lines[i+1:]
        elif date_location != -1:
            lines=lines[date_location+1:]

        #remove footer
        footer_found=False
        for i in range(len(lines))[-25:]:
            line=lines[i]
            line=line.strip()
            line=punctuation.sub('',lines[i].lower())

            if 'fade out' in line or line.replace('the','').strip() == 'end':
                footer_found=True
                break

        if footer_found:
            lines=lines[:i]

        cleaned_script='\n'.join(lines)

        return cleaned_script

    def parse(self, script):
#        root=etree.Element("script", name=movie_name))

        whitespace = re.compile(r'^[\s]+')
        punctuation = re.compile(r'['+string.punctuation+']')
        pagenumber = re.compile(r'^[(]?\d{1,3}[)]?[\.]?$')
        speakermode = re.compile(r'\'s voice$|\'s voices$|\' voice$|\
            \' voices$|\'s voice-over$|\' voice-over$|\'s voice over$', re.IGNORECASE)
        speakermodeinbraces = re.compile(r'\(.*\)')
        utterancemodeinbraces = re.compile(r'^\(.*?\)')
        specialchars = re.compile(r'[^\w\s ]*')
        allspecialchars = re.compile(r'^[^\w\s ]*$')
        location = re.compile(r'\d{0,4}[ ]*int[\. ].*|\d{0,4}[ ]*interior.*\
            |\d{0,4}[ ]*ext[\. ].*|\d{0,4}[ ]*exterior.*')
        
        script=script.replace('\t', '    ')
        script=self.remove_header_and_footer(script)

        lines=[]
        min_indent=9999
        #parse file once to cleanup
        for line in script.split('\n'):
            line_copy=line
            #get indent size for this movie
            match=whitespace.match(line)
            if match!=None:
                cur_indent=match.span()[1]-match.span()[0]
                if cur_indent<min_indent:
                    min_indent=cur_indent
            else:
                min_indent=0

            line=line.lower().strip()

            #skip lines with one char since they're likely typos
            if len(line)==1:
                if line.lower() != 'a' or line.lower() != 'i':
                    continue

            #skip lines that describe movie setting: interior or exterior
            if location.match(line):
                continue

            #skip lines containing page numbers
            if pagenumber.match(line):
                continue

            #skip lines containing just special characters
            if line != '' and allspecialchars.match(line):
                continue

            #todo: skip direction lines

            lines.append(line_copy)            

        i=0 
        context=[]
        parsed_lines=[]

        while i<len(lines):
            line=lines[i]
            line=line[min_indent:]
            line_copy=line
            i+=1

            if line.strip()=='':
                continue

            if i==len(lines):
                context.append(line.strip())
                break

            if len(line.lstrip()) < len(line)/2.0 or \
                len(speakermodeinbraces.sub('',line).strip().split())<=3:
                found_speaker=True
                speaker=line.strip()
                utterance_list=[]
                line=lines[i]
                while line.strip() != '' and i<len(lines):
                    line=speakermodeinbraces.sub('',line).strip()
                    utterance_list.append(line.strip())
                    i+=1
                    if i==len(lines):
                        break
                    line=lines[i]

                if len(utterance_list) == 0:
                    context.append(lines[i-1].strip())
                else:
                    speaker=speaker.replace(':', '')
                    speaker=speaker.replace('O.S.', '')
                    speaker=speaker.replace('V.O.', '')
                    speaker=speakermodeinbraces.sub('',speaker).strip()
                    speaker=speakermode.sub('', speaker).strip()
                    utterance=utterancemodeinbraces.sub('',' '.join(utterance_list))
                    if speaker != '' and len(speaker.split())<=2:
                        parsed_lines.append('##### {0}'.format(' '.join(context)))
                        parsed_lines.append('{0} => {1}'.\
                            format(speaker, utterance))
                        context=[]

            else:
                context.append(line.strip()) 

        if len(context) != 0:
            parsed_lines.append('##### {0}'.format(' '.join(context)))

        return '\n'.join(parsed_lines)

    def process(self):
        in_ptr=open(self.scriptfile)
        script=in_ptr.read()
        in_ptr.close()

        formatted_script=self.parse(script)

        if len(formatted_script.split('\n')) > 10:
            out_ptr=open(self.outfile, 'w')
            out_ptr.write(formatted_script)
            out_ptr.close()

if __name__ == '__main__':
    html_dir = '../Data/scripts_html'
    text_dir = '../Data/scripts_txt'
    out_dir = '../Data/parsed_scripts'

    if len(sys.argv)>1:
        files=sys.argv[1:]
    else:
        print("Please provide a file name to be parsed")
        sys.exit(0)

    for file in files:
        filepath=os.path.join(text_dir, file)
        outpath=os.path.join(out_dir, file)
        p=script_parser(filepath, outpath)
        p.process()
        print("Done parsing {0}".format(file))
