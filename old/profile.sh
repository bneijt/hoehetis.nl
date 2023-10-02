#!/bin/bash
set -e
cd "`dirname "$0"`"
. virtualenv/bin/activate
python src/gen_profile.py 2>&1 | tee profile.log

