#! /bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

AWS_PROFILE=$(source ./get-aws-profile-name.sh)
echo "*** Using $AWS_PROFILE for deployment ***"

# Verify that layers/route_optimization/python exists and is not empty
if [ ! -d "lib/layers/route_optimization/python" ] || [ -z "$(ls -A lib/layers/route_optimization/python)" ]; then
  echo "Route Optimization Lambda Layer must firstly be created before deploying: Run in lib: ./create-route-optimization-layer.sh"
  exit 1
fi  

#--require-approval never
export RUNNINGDINNER_FUNCTIONS_STAGE="$1"
aws-vault exec "$AWS_PROFILE" -- cdk deploy --verbose --context region=eu-central-1 RouteOptimizationStack
