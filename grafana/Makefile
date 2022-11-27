export PATH := ../venv/bin:$(PATH)
export PYTHONDONTWRITEBYTECODE := 1

SOURCES = $(wildcard *.dashboard.py)

.PHONY: all
all: $(SOURCES:.dashboard.py=.json)

%.json: %.dashboard.py
	@cd .. && $(MAKE) _venv
	generate-dashboard --output $@ $<;

.PHONY: clean
clean:
	$(RM) -r venv *.json
