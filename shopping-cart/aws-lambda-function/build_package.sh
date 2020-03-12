#!/bin/bash

STATEFUN_PYTHON_SDK_WHL=${STATEFUN_PYTHON_SDK_WHL}

if [ -z "${STATEFUN_PYTHON_SDK_WHL}" ]; then
	echo "STATEFUN_PTYHON_SDK_WHL was not set"
	exit 1
fi

set -e

protoc --python_out=. --proto_path=../../protobuf/inventory/ ../../protobuf/inventory/inventory.proto
protoc --python_out=. --proto_path=../../protobuf/shopping-cart/ ../../protobuf/shopping-cart/shopping_cart.proto

rm -rf package
mkdir -p package
cd package

mkdir -p dependencies

pip3 install --target ./dependencies ${STATEFUN_PYTHON_SDK_WHL}
pip3 install --target ./dependencies protobuf

cd dependencies

zip -r9 ../shopping-cart-lambda-function.zip .

cd ../
rm -rf dependencies

cd ../

zip -g package/shopping-cart-lambda-function.zip user_shopping_cart.py
zip -g package/shopping-cart-lambda-function.zip shopping_cart_pb2.py
zip -g package/shopping-cart-lambda-function.zip inventory_pb2.py
