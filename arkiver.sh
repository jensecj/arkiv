#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: arkiver <url> [<url2>...]"
    exit 1
fi

source "venv/bin/activate"

for file in $@
do
    printf "\n"
    python3 app/app.py "$file"
    printf "\n"
done
