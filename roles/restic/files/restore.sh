#!/bin/sh -ae

lock_file=/var/lib/restic/restored

if [ -e "$lock_file" ]; then
	echo "backup already restored"
	exit
fi

. /etc/default/restic
if ! output=$(restic restore latest --target=/ --verify); then
	exit 1
fi
if printf '%s\n' "$output" | grep -Eq 'There were [0-9]+ errors'; then
	exit 1
fi

mkdir -p "$(dirname "$lock_file")"
touch "$lock_file"
