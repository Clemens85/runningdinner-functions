#! /bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

AWS_PROFILE=$(source ./get-aws-profile-name.sh)
echo "*** Using $AWS_PROFILE for deployment ***"

#--require-approval never
export GEOCODING_STAGE="$1"
aws-vault exec "$AWS_PROFILE" -- cdk deploy --verbose --context region=eu-central-1
