#!/usr/bin/env bash

rm -rf ../Data/scripts_txt/*
rm -rf ../Data/utterances_with_charnames/*
rm -rf ../Data/speaker_counts/*
./fetch_and_parse_sripts.py True
./get_speaker_counts.sh
