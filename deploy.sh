#!/bin/bash
git archive --format tar --prefix=hoehetis.nl/ HEAD | ssh localhost 'tar -x -C /tmp'
