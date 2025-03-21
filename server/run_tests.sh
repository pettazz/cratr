#!/usr/bin/env bash

mydir="$(cd "$(dirname "$0")" && pwd)"

python -m unittest -b test/test*