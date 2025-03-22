#!/usr/bin/env bash

mydir="$(cd "$(dirname "$0")" && pwd)"

echo "----------------------------"
echo " copying files to build dir"
echo "----------------------------"
rm -r dist
mkdir -p dist/deps

cp *.py *.sql config.yaml ../classifier-definitions.json dist/deps
pip install -r requirements.txt --target ./dist/deps
cd dist/deps

echo "----------------------------"
echo "        building zip"
echo "----------------------------"
zip -rX ../lambda-package.zip . -x "*/\.DS_Store" "*/__pycache__/*"

# todo: injecting gh secrets 

echo "----------------------------"
echo "         deploying"
echo "----------------------------"
aws lambda update-function-code\
    --profile default\
    --function-name cratr\
    --zip-file "fileb://$mydir/dist/lambda-package.zip"\
    --output json \
  | jq -r '.LastUpdateStatus'

cd $mydir