HOSTS := $(shell grep -Eoi '^[a-z]\S+' hosts | sort -u)

ANSIBLE ?= docker container run \
	--rm \
	--interactive \
	--tty \
	--volume $(CURDIR):/data \
	--workdir /data \
	--volume $(HOME)/.ssh:/root/.ssh \
	--volume $(realpath $(HOME)/.ssh/config):/root/.ssh/config \
	--volume /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock \
	--env SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock \
	ansible ansible

.SILENT:

_help:
	echo usage:
	printf '  make %s\n' $(HOSTS)

$(HOSTS): _secrets _image _lint
	$(ANSIBLE)-playbook --limit $@ main.yml

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
	docker image build --tag ansible .

_lint:
	$(ANSIBLE)-lint -qq --strict
