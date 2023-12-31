#!/bin/bash
set -e
cd "$(dirname "$0")"
if [[ -z "${OPENAI_API_KEY}" ]]; then
  echo "OPENAI_API_KEY is not set"
  exit 1
fi

TODAY=$(date +"%Y-%m-%d")

docker-compose up
git add public
git commit -am "Update $TODAY"
git push
