#!/bin/bash
export LC_CTYPE=en_US.utf-8
set -e
cd "`dirname "$0"`"
. virtualenv/bin/activate
python src/gen.py 2>&1 | tee run.log
