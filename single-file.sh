#!/bin/bash

if [ $# -lt 2 ]; then
    echo "usage: single-file.sh <url> <output html file>"
    exit 1
fi

url="$1"
out_file="$2"

node ./lib/SingleFile/cli/single-file --browser-executable-path /usr/bin/chromium "$url" "$out_file"
