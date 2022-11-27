export LC_ALL := C.UTF-8
export PATH := venv/bin:$(PATH)

ROLES = $(notdir $(wildcard roles/*))
HOSTS = $(shell grep -Eoi '^[a-z]\S+' hosts | sort -u)

.SILENT:

_help:
	echo USAGE
	printf '  %s\n' 'make HOST=HOST ROLE...'
	echo
	echo HOSTS
	printf '  %s\n' $(HOSTS)
	echo
	echo ROLES
	printf '  %s\n' $(ROLES)

$(ROLES): | HOST=$(HOST) _secrets _venv _lint
	echo '[{ hosts: [$(HOST)], roles: [$@] }]' | \
	ansible-playbook /dev/stdin

$(addprefix HOST=,$(HOSTS)):

_secrets:
	for secret in $$(grep -Eor '^(.+):.+secret_\1' *_vars | cut -d: -f1,2); do \
		file="$${secret%%.*}_secrets.yml"; \
		var="secret_$${secret##*:}"; \
		grep -sq "^$$var: " "$$file" && continue; \
		printf "$$secret: "; \
		read -r value; \
		echo "$$var: $$value" >> "$$file"; \
	done

_venv:
	test -d venv && exit 0; \
	python3 -m venv venv; \
	pip install --requirement requirements.txt

_lint:
	ansible-lint -qq --strict;
