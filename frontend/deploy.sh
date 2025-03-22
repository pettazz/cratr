#!/usr/bin/env bash

mydir="$(cd "$(dirname "$0")" && pwd)"

# npm run build
rm -r dist
mkdir dist
cp index.html dist

aws s3 sync ./dist s3://cratr-site\
 --delete\
 --exclude ".DS_Store"\
 --output json

aws cloudfront create-invalidation\
  --distribution-id=$AWSENV_CF_DISTRIBUTION\
  --paths /\*\
  --output json\
  | jq -r '.Invalidation'