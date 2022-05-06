#!/bin/sh -ae

HOSTNAME=$1

lock_file=/var/lib/restic/restored

if [ -e "$lock_file" ]; then
    echo "backup already restored"
    exit
fi

. /etc/default/restic
restic restore --target / latest
mkdir -p "$(dirname "$lock_file")"
touch "$lock_file"
