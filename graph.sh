#!/bin/bash
export LC_CTYPE=en_US.utf-8
export PATH=$PATH:/bin:/usr/bin

set -e
cd "`dirname "$0"`"
. virtualenv/bin/activate
python src/graph.py
# 2>&1 | tee run.log
