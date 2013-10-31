#!/bin/bash
cd "`dirname "$0"`"
. virtualenv/bin/activate
python -m unittest discover src '*_test.py'
