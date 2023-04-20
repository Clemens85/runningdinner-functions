#! /bin/bash

CUR_DIR=$(pwd)
cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1

ENDPOINT_PARAM=""
if [[ "--local" == "$1" ]]; then
  ENDPOINT_PARAM='--endpoint-url http://127.0.0.1:4566'
fi

VALUE=$(aws ssm get-parameter --name "/runningdinner/googlemaps/apikey" --with-decryption --query "Parameter.Value" --output text $ENDPOINT_PARAM)
if [[ -z "$VALUE" ]]; then
  echo "Could not fetch google maps API key from local SSM parameter store"
  exit 1
fi

echo "GOOGLE_MAPS_API_KEY=$VALUE" > ../.env

cd $CUR_DIR
