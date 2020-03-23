import subprocess
import glob
import os
import numpy as np
import argparse

#------------------------------------------------------------------------------------
# PROCESS ARGUMENTS
#------------------------------------------------------------------------------------
def read_args():
	parser = argparse.ArgumentParser(description='Script that parses a movie script pdf into its constituent classes')
	parser.add_argument("-i", "--input", help="Path to script PDF to be parsed", required=True)
	parser.add_argument("-o", "--output", help="Path to directory for saving output", required=True)
	args = parser.parse_args()
	return os.path.abspath(args.input), os.path.abspath(args.output)

if __name__ == "__main__":
	#------------------------------------------------------------------------------------
	# DEFINE
	#------------------------------------------------------------------------------------
	file_orig, save_dir = read_args()
	tag_set = ['S', 'N', 'C', 'D', 'E', 'T', 'M']
	meta_set = ['BLACK', 'darkness']
	bound_set = ['INT.', 'EXT.']
	trans_set = ['CUT TO']
	char_max_words = 7
	#------------------------------------------------------------------------------------
	# CONVERT PDF TO TEXT
	#------------------------------------------------------------------------------------
	file_name = file_orig.replace('.pdf', '.txt')
	subprocess.call('pdftotext -layout ' + file_orig + ' ' + file_name, shell=True)
	# READ TEXT FILE
	fid = open(file_name, 'r')
	script_orig = fid.read().splitlines()
	fid.close()
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
	# STAGE 1: DETECT METADATA
	# (LOOK FOR CONTENT PRECEDING SPECIFIC PHRASES THAT INDICATE BEGINNING OF MOVIE)
	#------------------------------------------------------------------------------------
	met_ind = []
	for i, x in enumerate(script_noind):
		if tag_vec[i] not in tag_set:
			if len(x.split()) > 0:
				z = []
				for y in x.split():
					z.append(''.join([c for c in y if c.isalnum()]))
                
				if len(set(z) & set(meta_set)) > 0:
					met_ind.append(i)
    
	if len(met_ind) > 0:
		for i, x in enumerate(script_noind[: met_ind[0]]):
			if len(x.split()) > 0:
				tag_vec[i] = 'M'
        
		tag_vec[met_ind[0]] = 'T'
    
	#------------------------------------------------------------------------------------
	# STAGE 2: DETECT SCENE BOUNDARIES
	# (LOOK FOR ALL-CAPS LINES CONTAINING "INT." OR "EXT.")
	#------------------------------------------------------------------------------------
	bound_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and \
														x.isupper() and x in bound_set]
	for x in bound_ind:
		tag_vec[x] = 'S'
    
	#------------------------------------------------------------------------------------
	# STAGE 3: DETECT CHARACTER-DIALOGUE BLOCKS
	# (CHARACTER IS ALL-CAPS LINE PRECEDED BY NEWLINE AND NOT FOLLOWED BY A NEWLINE)
	# (DIALOGUE IS WHATEVER IMMEDIATELY FOLLOWS CHARACTER)
	# (EITHER CHARACTER OR DIALOGUE MIGHT CONTAIN DILAOGUE METADATA; WILL BE DETECTED LATER)
	#------------------------------------------------------------------------------------
	char_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()\
														and script_noind[i - 1] == ''\
														and script_noind[i + 1] != ''\
														and len(x.split()) < char_max_words]
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
	# STAGE 4: DETECT TRANSITIONS
	# (LOOK FOR ALL-CAPS LINES PRECEDED BY NEWLINE, FOLLOWED BY NEWLINE AND CONTAINING "CUT TO")
	#------------------------------------------------------------------------------------
	trans_ind = [i for i, x in enumerate(script_noind) if tag_vec[i] not in tag_set and x.isupper()\
														and script_noind[i - 1] == ''\
														and script_noind[i + 1] == ''\
														and x in trans_set]
	for x in trans_ind:
		tag_vec[x] = 'T'
    
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
	save_name = save_dir + '/' + file_name.split('/')[-1].strip('.txt') + '_parsed.txt'
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
					if '(' in combined_str:
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
	fid = open(save_name, 'r')
	parsed_script = fid.read().splitlines()
	fid.close()
	abridged_name = save_name.strip('.txt') + '_abridged.txt'
	fid = open(abridged_name, 'w')
	abridged_script = [x for x in parsed_script if x.startswith('C') or x.startswith('D')]
	for i in range(0, len(abridged_script), 2):
		char_str = ' '.join(abridged_script[i].split('C:')[1].split())
		dial_str = ' '.join(abridged_script[i + 1].split('D:')[1].split())
		fid.write(''.join([char_str, '=>', dial_str, '\n']))
    
	fid.close()