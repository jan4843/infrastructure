CONTAINER = docker container run \
	--rm --interactive --tty \
	--volume $(CURDIR):/data:ro \
	--workdir /data \
	--volume $(HOME)/.ssh:/root/.ssh:ro \
	--volume $(realpath $(HOME)/.ssh/config):/root/.ssh/config:ro \
	--volume /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock:ro \
	--env SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock \
	ansible

ifndef host
host = $(error Missing value for variable `host')
endif

tags ?= all

.SILENT:

run: _secrets _image _lint
	$(CONTAINER) ansible-playbook main.yml \
		--limit $(host) \
		--tags $(tags)

debug: _image
	$(CONTAINER) ansible $(host) \
		--module-name ansible.builtin.setup
	$(CONTAINER) ansible $(host) \
		--module-name ansible.builtin.debug \
		--args var=hostvars[inventory_hostname]

shell: _image
	$(CONTAINER) bash

clean:
	! docker image inspect ansible >/dev/null 2>&1 || \
	docker image rm ansible

_lint: _image
	$(CONTAINER) ansible-lint -qq --strict --offline

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
	docker image inspect ansible >/dev/null 2>&1 || \
	docker image build --tag ansible .
