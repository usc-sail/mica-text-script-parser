import subprocess
import glob
import os
import numpy as np
import argparse
import re

#------------------------------------------------------------------------------------
# REMOVE NON-ALPHANUMERIC CHARACTERS FROM STRING
#------------------------------------------------------------------------------------
def read_args():
	parser = argparse.ArgumentParser(description='Script that parses a movie script pdf/txt into its constituent classes')
	parser.add_argument("-i", "--input", help="Path to script PDF/TXT to be parsed", required=True)
	parser.add_argument("-o", "--output", help="Path to directory for saving output", required=True)
	parser.add_argument("-a", "--abridged", help="Print abridged version (on/off)", default='off')
	args = parser.parse_args()
	if args.abridged not in ['on', 'off']: raise AssertionError("Invalid value. Choose either off or on")
	return os.path.abspath(args.input), os.path.abspath(args.output), args.abridged


#------------------------------------------------------------------------------------
# PROCESS ARGUMENTS
#------------------------------------------------------------------------------------
def read_args():
	parser = argparse.ArgumentParser(description='Script that parses a movie script pdf/txt into its constituent classes')
	parser.add_argument("-i", "--input", help="Path to script PDF/TXT to be parsed", required=True)
	parser.add_argument("-o", "--output", help="Path to directory for saving output", required=True)
	parser.add_argument("-a", "--abridged", help="Print abridged version (on/off)", default='off')
	args = parser.parse_args()
	if args.abridged not in ['on', 'off']: raise AssertionError("Invalid value. Choose either off or on")
	return os.path.abspath(args.input), os.path.abspath(args.output), args.abridged

def parse(file_orig, save_dir, abr_flag, save_name=None, abridged_name=None):
	#------------------------------------------------------------------------------------
	# DEFINE
	#------------------------------------------------------------------------------------
	tag_set = ['S', 'N', 'C', 'D', 'E', 'T', 'M']
	meta_set = ['BLACK', 'darkness']
	bound_set = ['INT. ', 'EXT. ']
	trans_set = ['CUT ', 'FADE ']
	char_max_words = 7
	meta_thresh = 2
	sent_thresh = 5
	trans_thresh = 5
	#------------------------------------------------------------------------------------
	# CONVERT PDF TO TEXT
	#------------------------------------------------------------------------------------
	if file_orig.endswith(".pdf"):
		file_name = file_orig.replace('.pdf', '.txt')
		subprocess.call('pdftotext -layout ' + file_orig + ' ' + file_name, shell=True)
	elif file_orig.endswith(".txt"):
		file_name = file_orig
	else:
		raise AssertionError("File should be either pdf or txt")
    
	# READ TEXT FILE
	fid = open(file_name, 'r')
	script_orig = fid.read().splitlines()
	fid.close()
	re_func = re.compile('[^a-zA-Z ]')
	#------------------------------------------------------------------------------------
	# REMOVE INDENTS
	#------------------------------------------------------------------------------------
	script_noind = []
	for script_line in script_orig:
		if len(script_line.split()) > 0:
			script_noind.append(' '.join(script_line.split()))
		else:
			script_noind.append('')
    
	num_lines = len(script_noind)
	tag_vec = np.array(['0' for x in range(num_lines)])
	#------------------------------------------------------------------------------------
	# STAGE 1: DETECT SCENE BOUNDARIES
	# (LOOK FOR ALL-CAPS LINES CONTAINING "INT." OR "EXT.")
	#------------------------------------------------------------------------------------
	bound_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and \
														x.isupper() and \
														any([y in x for y in bound_set])]
	if len(bound_ind) > 0:
		for x in bound_ind:
			tag_vec[x] = 'S'
    
	#------------------------------------------------------------------------------------
	# STAGE 2: DETECT TRANSITIONS
	# (LOOK FOR ALL-CAPS LINES PRECEDED BY NEWLINE, FOLLOWED BY NEWLINE AND CONTAINING "CUT " OR "FADE ")
	#------------------------------------------------------------------------------------
	trans_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()\
														and len(re_func.sub('', x).split()) < trans_thresh\
														and any([y in x for y in trans_set])]
	if len(trans_ind) > 0:
		for x in trans_ind:
			tag_vec[x] = 'T'
    
	#------------------------------------------------------------------------------------
	# STAGE 3: DETECT METADATA
	# (LOOK FOR CONTENT PRECEDING SPECIFIC PHRASES THAT INDICATE BEGINNING OF MOVIE)
	#------------------------------------------------------------------------------------
	met_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set\
														and i != 0 and i != (len(script_noind) - 1)\
														and len(x.split()) < meta_thresh\
														and re_func.sub('', script_noind[i - 1]) == ''\
														and re_func.sub('', script_noind[i + 1]) == ''\
														and any([y in x for y in meta_set])]
	sent_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set\
														and i != 0 and i != (len(script_noind) - 1)\
														and len(x.split()) > sent_thresh\
														and script_noind[i - 1] == ''\
														and script_noind[i + 1] != '']
	meta_ind = sorted(met_ind + bound_ind + trans_ind + sent_ind)
	if len(meta_ind) > 0:
		for i, x in enumerate(script_noind[: meta_ind[0]]):
			if len(x.split()) > 0:
				tag_vec[i] = 'M'
    
	#------------------------------------------------------------------------------------
	# STAGE 4: DETECT CHARACTER-DIALOGUE BLOCKS
	# (CHARACTER IS ALL-CAPS LINE PRECEDED BY NEWLINE AND NOT FOLLOWED BY A NEWLINE)
	# (DIALOGUE IS WHATEVER IMMEDIATELY FOLLOWS CHARACTER)
	# (EITHER CHARACTER OR DIALOGUE MIGHT CONTAIN DILAOGUE METADATA; WILL BE DETECTED LATER)
	#------------------------------------------------------------------------------------
	char_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()\
														and i != 0 and i != (len(script_noind) - 1)\
														and script_noind[i - 1] == ''\
														and script_noind[i + 1] != ''\
														and len(x.split()) < char_max_words]
	len(char_ind)
	for x in char_ind:
		tag_vec[x] = 'C'
		dial_flag = 1
		while dial_flag > 0:
			if script_noind[x + dial_flag] != '':
				tag_vec[x + dial_flag] = 'D'
				dial_flag += 1
			else:
				dial_flag = 0
    
	#------------------------------------------------------------------------------------
	# STAGE 5: DETECT SCENE DESCRIPTION
	# (LOOK FOR REMAINING LINES THAT ARE NOT PAGE BREAKS)
	#------------------------------------------------------------------------------------
	desc_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x != ''\
															and not x.strip('.').isdigit()]
	for x in desc_ind:
		tag_vec[x] = 'N'
    
	#------------------------------------------------------------------------------------
	# REMOVE UN-TAGGED LINES
	#------------------------------------------------------------------------------------
	tag_valid = []
	script_valid = []
	for i, x in enumerate(tag_vec):
		if x != '0':
			tag_valid.append(x)
			script_valid.append(script_noind[i])
    
	#------------------------------------------------------------------------------------
	# WRITE PARSED SCRIPT TO FILE
	#------------------------------------------------------------------------------------
	if save_name is None:
		save_name = os.path.join(save_dir, file_name.split('/')[-1].rstrip('.txt') + '_parsed.txt')
	else:
		save_name = os.path.join(save_dir, save_name)
		
	fid = open(save_name, 'w')
	for i, x in enumerate(tag_valid):
		if x in ['M', 'T', 'S']:
			# WRITE METADATA, TRANSITION AND SCENE BOUNDARY LINES AS THEY ARE
			fid.write(''.join([x, ': ', script_valid[i], '\n']))
		elif x in ['C', 'D', 'N']:
			# IF CHARACTER, DIALOGUE OR SCENE DESCRIPTION CONSIST OF MULTIPLE LINES, COMBINE THEM
			if i == 0 or x != tag_valid[i - 1]:
				# INITIALIZE IF FIRST OF MULTIPLE LINES
				to_combine = []
            
			to_combine += script_valid[i].split()
			if i == (len(tag_valid) - 1) or x != tag_valid[i + 1]:
				combined_str = ' '.join(to_combine)
				if x == 'N':
					# IF SCENE DESCRIPTION, WRITE AS IT IS
					fid.write(''.join([x, ': ', combined_str, '\n']))
				else:
					if '(' in combined_str and ')' in combined_str:
						# IF DIALOGUE METADATA PRESENT, EXTRACT IT
						split_1 = combined_str.split('(')
						split_2 = split_1[1].split(')')
						dial_met = split_2[0]
						rem_str = split_1[0] + split_2[1]
						if x == 'C':
							# IF CHARACTER, APPEND DIALOGUE METADATA
							fid.write(''.join([x, ': ', ' '.join(rem_str.split()), '\n']))
							fid.write(''.join(['E: ', dial_met, '\n']))
						elif x == 'D':
							# IF DIALOGUE, PREPEND DIALOGUE METADATA
							fid.write(''.join(['E: ', dial_met, '\n']))
							fid.write(''.join([x, ': ', ' '.join(rem_str.split()), '\n']))
                    
					else:
						# IF NO DIALOGUE METADATA, WRITE AS IT IS
						fid.write(''.join([x, ': ', combined_str, '\n']))
    
	fid.close()
	#------------------------------------------------------------------------------------
	# CREATE CHARACTER=>DIALOGUE ABRIDGED VERSION
	#------------------------------------------------------------------------------------
	if abr_flag == 'on':
		fid = open(save_name, 'r')
		parsed_script = fid.read().splitlines()
		fid.close()
		if abridged_name is None:
			abridged_name = save_name.rstrip('.txt') + '_abridged.txt'
		else:
			abridged_name = os.path.join(save_dir, abridged_name)
		fid = open(abridged_name, 'w')
		abridged_script = [x for x in parsed_script if x.startswith('C') or x.startswith('D')]
		for i in range(0, len(abridged_script), 2):
			char_str = ' '.join(abridged_script[i].split('C:')[1].split())
			dial_str = ' '.join(abridged_script[i + 1].split('D:')[1].split())
			fid.write(''.join([char_str, '=>', dial_str, '\n']))
        
		fid.close()

if __name__ == "__main__":
	file_orig, save_dir, abr_flag = read_args()
	parse(file_orig, save_dir, abr_flag)