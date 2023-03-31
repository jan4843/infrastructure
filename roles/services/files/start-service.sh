#!/bin/sh -e

cd "$1"

if [ -e Makefile ]; then
	make install
fi

docker compose up --detach
