#!/bin/sh -e

SERVICES_ROOT=$1

exit_code=0

for service in "$SERVICES_ROOT/"*/; do
    cd "$service"
    service=$(basename "$PWD")
    config=$(docker compose config 2> /dev/null) || continue

    if echo "$config" | grep -Eq 'restart: (always|unless-stopped|on-failure)'; then
        printf '%s\n' "$service"

        if [ -z "$(docker compose ps -q)" ]; then
            # service is not already running, notify via exit code
            exit_code=100
        fi
    fi
done

exit "$exit_code"
