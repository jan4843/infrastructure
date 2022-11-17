ANSIBLE_VERSION ?= 6.6.*
ANSIBLE_LINT_VERSION ?= 6.8.*

ANSIBLE ?= docker run --rm --interactive --tty \
	--volume "$(HOME)/.ssh:/root/.ssh:ro" \
	--volume "$(CURDIR):/data:ro" \
	--volume "$(CURDIR)/roles:/etc/ansible/roles:ro" \
	--workdir "/data" \
	ansible \
	ansible

roles = $(notdir $(wildcard roles/*))
hosts = $(shell grep -Eoi '^[a-z]\S+' hosts | sort -u)

.SILENT:

_help:
	echo USAGE
	printf '  %s\n' 'make HOST=HOST ROLE...'
	echo; echo HOSTS
	printf '  %s\n' $(hosts)
	echo; echo ROLES
	printf '  %s\n' $(roles)

$(roles): _noop HOST=$(HOST) _secrets _image _lint
	echo '[{ hosts: [$(HOST)], roles: [$@] }]' > .git/playbook.yml
	$(ANSIBLE)-playbook --inventory hosts .git/playbook.yml

_noop:

$(addprefix HOST=,$(hosts)):

_secrets:
	for secret in $$(grep -Eor '^(.+):.+secret_\1' *_vars | cut -d: -f1,2); do \
		file="$${secret%%.*}_secrets.yml"; \
		var="secret_$${secret##*:}"; \
		grep -sq "^$$var: " "$$file" && continue; \
		printf "$$secret: "; \
		read -r value; \
		echo "$$var: $$value" >> "$$file"; \
	done

_image:
	docker image inspect ansible > /dev/null 2>&1 || \
	printf "FROM python:3\nRUN pip install --no-cache-dir ansible==$(ANSIBLE_VERSION) ansible-lint==$(ANSIBLE_LINT_VERSION)" | \
	docker build --tag ansible -

_lint:
	$(ANSIBLE)-lint -qq --strict
