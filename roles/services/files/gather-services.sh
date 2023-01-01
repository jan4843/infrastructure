#!/bin/sh -e

for service in "$1"/*/; do
	test -d "$service" || continue
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

exit $exit_code
