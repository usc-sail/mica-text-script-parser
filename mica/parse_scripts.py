import sys
import os
import re
import string
from lxml import etree

class script_parser:
    def __init__(self, scriptfile, outfile, write = True, verbose = False):
        self.scriptfile=scriptfile
        self.outfile=outfile
        self.write = write
        self.verbose = verbose

    def is_scene_boundary(self, line):
        return ("INT" in line or "EXT" in line) and line.isupper()

    def remove_header_and_footer(self, script):
        lines=script.split('\n')
        n_header_lines = 0
        n_footer_lines = 0

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
        n_header_lines = len(lines)
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
        n_header_lines = n_header_lines - len(lines)

        #remove footer
        n_footer_lines = len(lines)
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
        n_footer_lines = n_footer_lines - len(lines)

        cleaned_script='\n'.join(lines)

        return cleaned_script, n_header_lines, n_footer_lines

    def parse(self, script):
#        root=etree.Element("script", name=movie_name))

        if self.verbose:
            n = len(script.split("\n"))
            print(f"#Lines in script        = {n:5d}\n")

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
        script, n_header_lines, n_footer_lines=self.remove_header_and_footer(script)
        if self.verbose:
            n = len(script.split("\n"))
            print(f"#Lines in script        = {n:5d}")
            print(f"#Lines in header        = {n_header_lines:5d}")
            print(f"#Lines in footer        = {n_footer_lines:5d}\n")

        lines=[]
        line_indices = []
        min_indent=9999
        #parse file once to cleanup
        for i, line in enumerate(script.split('\n')):
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
            # if location.match(line):
                # continue

            #skip lines containing page numbers
            if pagenumber.match(line):
                continue

            #skip lines containing just special characters
            if line != '' and allspecialchars.match(line):
                continue

            #todo: skip direction lines

            lines.append(line_copy)
            line_indices.append(i)            

        if self.verbose:
            print(f"#Lines in lines         = {len(lines):5d}")
            print(f"#Lines in line indices  = {len(line_indices):5d}\n")

        i=0 
        context=[]
        parsed_lines=[]
        annotation_label_sequence = ""

        while i<len(lines):
            line=lines[i]
            line=line[min_indent:]
            line_copy=line
            i+=1

            if line.strip()=='':
                annotation_label_sequence += " "
                continue

            if i==len(lines):
                annotation_label_sequence += " "
                context.append(line.strip())
                break

            if self.is_scene_boundary(line):
                annotation_label_sequence += "S"
                parsed_lines.append("##### {}".format(line.strip()))

            elif len(line.lstrip()) < len(line)/2.0 or len(speakermodeinbraces.sub('',line).strip().split())<=3:
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
                    annotation_label_sequence += " "
                    context.append(lines[i-1].strip())
                else:
                    speaker=speaker.replace(':', '')
                    speaker=speaker.replace('O.S.', '')
                    speaker=speaker.replace('V.O.', '')
                    speaker=speakermodeinbraces.sub('',speaker).strip()
                    speaker=speakermode.sub('', speaker).strip()
                    utterance=utterancemodeinbraces.sub('',' '.join(utterance_list))
                    if speaker != '' and len(speaker.split())<=2:
                        annotation_label_sequence += "C"
                        annotation_label_sequence += "D"*len(utterance_list)
                        # parsed_lines.append('##### {0}'.format(' '.join(context)))
                        parsed_lines.append('\t\t{0} => {1}'.format(speaker, utterance))
                        context=[]
                    else:
                        annotation_label_sequence += " " + " "*len(utterance_list)

            else:
                annotation_label_sequence += " "
                context.append(line.strip()) 

        # if len(context) != 0:
            # parsed_lines.append('##### {0}'.format(' '.join(context)))

        if self.verbose:
            print(f"#Length of annotation   = {len(annotation_label_sequence):5d}\n")

        label_sequence = [" "] * len(script.split("\n"))
        for i, line_index in enumerate(line_indices):
            label_sequence[line_index] = annotation_label_sequence[i]
        label_sequence = "".join(label_sequence)
        label_sequence = " "*n_header_lines + label_sequence + " "*n_footer_lines

        if self.verbose:
            print(f"Length of annotation    = {len(label_sequence):5d}\n\n")

        return '\n'.join(parsed_lines), label_sequence

    def process(self):
        in_ptr=open(self.scriptfile)
        script=in_ptr.read()
        in_ptr.close()

        formatted_script, label_sequence =self.parse(script)

        if self.write and len(formatted_script.split('\n')) > 10:
            out_ptr=open(self.outfile, 'w')
            out_ptr.write(formatted_script)
            out_ptr.close()

        return label_sequence

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
