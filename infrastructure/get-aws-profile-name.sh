#! /bin/bash

stage=$1
if [[ -z "$stage" ]]; then
  echo "Error: Must pass a stage as first parameter"
  exit 1
fi

echo "runningdinner-${stage}-admin"