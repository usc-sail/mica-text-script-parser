#!/usr/bin/env bash

rm -rf ../Data/scripts_txt/*
rm -rf ../Data/utterances_with_charnames/*
rm -rf ../Data/speaker_counts/*
./a_01_fetch_extract_and_parse.py True
./get_speaker_counts.sh
