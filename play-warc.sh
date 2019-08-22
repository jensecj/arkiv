#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: play-warc <warc archive>"
    exit 1
fi

warc="$1"
warc_path=$(dirname "$warc")
warc_base=$(basename "$warc")

url=$(zcat "$warc" | grep "WARC-Target-URI" | head -n 1 | cut -d' ' -f2)
url_path=$(echo "$url" | sed 's/.*\/\///')

if [ -z "$url" ]; then
    echo "error: archive url not found!"
    exit 1
fi

echo "found archive url: $url"

python -m warcat verify "$warc"

echo "extracting archive..."
tmpfolder=$(mktemp -d)

# python -m warcat --output-dir "$tmpfolder" --progress extract "$warc"
warcex -path "$warc_path" -string "$warc_base" -dump content -output_path "$tmpfolder"

ls "$tmpfolder"

printf "\n\n"
echo "To browse archive, visit: http://localhost:8080/$url_path"
printf "\n\n"

http-server "$tmpfolder" -c-1 -o "http://127.0.0.1:8080/$url_path"
