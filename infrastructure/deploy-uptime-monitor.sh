#! /bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

if [[ -z "$1" ]]; then
  echo "Usage: $0 <dev|prod>"
  exit 1
fi

AWS_PROFILE=$(source ./get-aws-profile-name.sh)
echo "*** Using $AWS_PROFILE for deployment ***"

export RUNNINGDINNER_FUNCTIONS_STAGE="$1"
aws-vault exec "$AWS_PROFILE" -- cdk deploy --verbose --context region=eu-central-1 UptimeMonitorStack