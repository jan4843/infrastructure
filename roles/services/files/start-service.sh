#!/bin/sh

cd "$1" || exit 1
make install
docker compose up --detach
