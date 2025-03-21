#!/usr/bin/env bash

mydir="$(cd "$(dirname "$0")" && pwd)"

rm -r dist
mkdir -p dist/deps

pip install -r requirements.txt --target ./dist/deps
cd dist/deps
zip -rX ../lambda-package.zip . -rX

cd $mydir
cp ../classifier-definitions.json .
zip -X dist/lambda-package.zip *.py config.yaml classifier-definitions.json

# todo: injecting gh secrets 

aws lambda update-function-code\
    --profile default\
    --function-name cratr\
    --zip-file "fileb://$mydir/dist/$lambda-package.zip"\
    --output json \
  | jq -r '.LastUpdateStatus'

rm -r dist