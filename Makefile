.DEFAULT_GOAL := all

.PHONY: all
all: clean lint run

.PHONY: lint
lint:
	yamllint -s inputs.yml
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 80 --check

.PHONY: run
run:
	python build_shk.py

.PHONY: clean
clean:
	find . -name "*.pyc" | xargs -r rm
	rm -rf outputs/
	rm -f *.zip
