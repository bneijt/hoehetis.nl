#!/bin/bash
git archive --format tar HEAD | ssh owl 'tar -x -C /srv/http/site/hoehetis.nl/'
