#!/bin/sh -e

DEVICE=$1
POOL_NAME=$2

zpool import -d "$DEVICE" "$POOL_NAME" ||
zpool import -d "$DEVICE" "$POOL_NAME" 2>&1 | grep -q already
