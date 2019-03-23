#!/usr/bin/env bash
 
cd ../Data

for i in `find ../Data/utterances_with_charnames/ -type f -exec basename {} \;`; do
    echo "$i"
    cat "utterances_with_charnames/$i" | awk -F '=>' '{ print $1 }' | sort | uniq -c | sort -r > "speaker_counts/$i"
done
