help:
	cat Makefile

setup:
	pre-commit install --install-hooks
	poetry install

################################################################################

.PHONY: \
	help
