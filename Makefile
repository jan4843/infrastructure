ANSIBLE ?= docker run --rm --interactive --tty \
	--volume "$(HOME)/.ssh:/root/.ssh:ro" \
	--volume "$(CURDIR):/data:ro" \
	--workdir "/data" \
	ansible \
	ansible

.SILENT:

help:
	echo usage:
	grep -Eoi '^[a-z]\S+' hosts | sort -u | sed 's/^/  make /'

%:
	$(MAKE) secrets image
	$(ANSIBLE)-playbook main.yml --limit $@

image:
	docker image inspect ansible > /dev/null 2>&1 || \
	printf "FROM alpine\nRUN apk add --no-cache ansible openssh-client" | \
	docker build --tag ansible -

secrets:
	for secret in $$(grep -Eor '^(.+):.+secret_\1' *_vars | cut -d: -f1,2); do \
		file="$${secret%%.*}_secrets.yml"; \
		var="secret_$${secret##*:}"; \
		grep -sq "^$$var: " "$$file" && continue; \
		printf "$$secret: "; \
		read -r value; \
		echo "$$var: $$value" >> "$$file"; \
	done
