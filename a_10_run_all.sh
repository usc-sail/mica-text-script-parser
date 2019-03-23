#!/usr/bin/env bash
 
rm -rf ../Data/utterances_with_charnames/*
rm -rf ../Data/speaker_counts/*
./a_01_fetch_extract_and_parse.py True
./a_02_get_speaker_counts.sh
