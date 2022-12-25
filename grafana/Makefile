export PATH := venv/bin:$(PATH)
export PYTHONDONTWRITEBYTECODE := 1

SOURCES := $(wildcard *.dashboard.py)

.PHONY: all
all: $(SOURCES:.dashboard.py=.json)

%.json: %.dashboard.py | venv
	generate-dashboard --output $@ $<;

venv: requirements.txt
	python3 -m venv venv
	pip install -r requirements.txt

.PHONY: clean
clean:
	$(RM) -r venv *.json
