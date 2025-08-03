#! /bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

AWS_PROFILE=$(source ./get-aws-profile-name.sh)
echo "*** Using $AWS_PROFILE for deployment ***"

# Name geocoding should have actually been named more generic, but it is as it is now
export RUNNINGDINNER_FUNCTIONS_STAGE="$1"
aws-vault exec "$AWS_PROFILE" -- cdk bootstrap --profile "$AWS_PROFILE" --toolkit-stack-name geocoding --context region=eu-central-1
