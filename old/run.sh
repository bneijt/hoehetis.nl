#!/bin/bash
export LC_CTYPE=en_US.utf-8
export PATH=$PATH:/bin:/usr/bin
set -e
renice 10 $$
cd "`dirname "$0"`"
ulimit -v 314572800
. virtualenv/bin/activate
python -OO src/gen.py 2>&1 | tee run.log
for f in www/*.html www/*.json; do
    gzip --to-stdout --best "$f" > "$f".gz || rm "$f".gz
done
cp -f favicon.png www/favicon.png
if [ ! -f www/robots.txt ]; then
    touch www/robots.txt
fi

