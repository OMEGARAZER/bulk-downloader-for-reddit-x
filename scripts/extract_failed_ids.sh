#!/bin/bash

if [ -e "$1" ]; then
    file="$1"
else
    echo "CANNOT FIND LOG FILE"
    exit 1
fi

{
    grep "Could not download submission" "$file" | awk '{ print $12 }' | rev | cut -c 2- | rev ;
    grep "Failed to download resource" "$file" | awk '{ print $15 }' ;
    grep "failed to download submission" "$file" | awk '{ print $14 }' | rev | cut -c 2- | rev ;
    grep "Failed to write file" "$file" | awk '{ print $14 }' ;
    grep "skipped due to disabled module" "$file" | awk '{ print $9 }' ;
}
