sources := $(wildcard *.dashboard.py)

export PATH := venv/bin:$(PATH)
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: all
all: $(sources:.dashboard.py=.json)

%.json: %.dashboard.py | venv
	generate-dashboard --output $@ $<

venv:
	python3 -m venv venv
	pip install -qq -r requirements.txt

.PHONY: clean
clean:
	$(RM) -r venv *.json
