#!/bin/bash

declare HOST=$1
declare TIMEOUT=$2

echo "Reaching host $1: "

curl --head -X GET --retry $TIMEOUT --retry-connrefused --retry-delay 1 $HOST