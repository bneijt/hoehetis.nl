#!/bin/bash
export LC_CTYPE=en_US.utf-8
export PATH=$PATH:/bin:/usr/bin

set -e
cd "`dirname "$0"`"
. virtualenv/bin/activate
python src/gen.py 2>&1 | tee run.log
for f in www/*.html www/*.json; do
    gzip --to-stdout --best "$f" > "$f".gz || rm "$f".gz
done
