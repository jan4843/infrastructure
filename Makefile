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

$(addprefix HOST=,$(hosts)):

$(roles): _noop HOST=$(HOST) _secrets _image
	echo '[{ hosts: [$(HOST)], roles: [$@] }]' > .git/playbook.yml
	$(ANSIBLE)-playbook --inventory hosts .git/playbook.yml

_noop:

_image:
	docker image inspect ansible > /dev/null 2>&1 || \
	printf "FROM alpine\nRUN apk add --no-cache ansible openssh-client" | \
	docker build --tag ansible -

_secrets:
	for secret in $$(grep -Eor '^(.+):.+secret_\1' *_vars | cut -d: -f1,2); do \
		file="$${secret%%.*}_secrets.yml"; \
		var="secret_$${secret##*:}"; \
		grep -sq "^$$var: " "$$file" && continue; \
		printf "$$secret: "; \
		read -r value; \
		echo "$$var: $$value" >> "$$file"; \
	done
