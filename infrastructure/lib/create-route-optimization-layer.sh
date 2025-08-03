#!/bin/bash

mkdir -p layers/route_optimization/python
rm -rf layers/route_optimization/python/*

docker run --rm -v "$PWD/layers/route_optimization":/lambda-layer -w /lambda-layer python:3.12-bookworm bash -c "
  pip install --platform manylinux2014_x86_64 --target=package --implementation cp --only-binary=:all: --upgrade scikit-learn numpy pydantic -t python
"

sudo chown -R $USER:$USER layers/route_optimization/python

find layers/route_optimization/python -type d -name "__pycache__" -exec rm -rf {} +
find layers/route_optimization/python -type d -name "tests" -exec rm -rf {} +
find layers/route_optimization/python -type d -name "*.dist-info" -exec rm -rf {} +
find layers/route_optimization/python -type d -name "*.egg-info" -exec rm -rf {} +