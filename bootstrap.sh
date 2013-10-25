#!/bin/bash
if [ ! -d "virtualenv" ]; then
    virtualenv -p `which python3` virtualenv
fi

. virtualenv/bin/activate
pip install feedparser
pip install Jinja2

echo '. virtualenv/bin/activate'

