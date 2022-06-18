#!/bin/sh -e

if [ "$(timedatectl show --property=Timezone)" = "Timezone=$1" ]; then
	echo "timezone already set"
	exit
fi

timedatectl set-timezone "$1"
