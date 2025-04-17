#! /bin/bash

set +e
CUR_DIR=$(pwd)

passedStage=$1
if [[ -z "$passedStage" ]]; then
  echo "Error: Must pass a stage as first parameter"
  exit 1
fi

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

source ../runningdinner-infrastructure/aws/scripts/setup-aws-cli.sh "$passedStage"

echo "Calling Deploy tp $passedStage..."
npx sls deploy --stage "$passedStage" --verbose

source ../runningdinner-infrastructure/aws/scripts/clear-aws-cli.sh

# shellcheck disable=SC2164
cd "$CUR_DIR"