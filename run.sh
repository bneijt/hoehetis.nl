#!/bin/bash
set -e
cd "`dirname "$0"`"
. virtualenv/bin/activate
python src/gen.py 2>&1 | tee run.log
