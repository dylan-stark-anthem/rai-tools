help:
	cat Makefile

setup:
	pre-commit install --install-hooks

################################################################################

.PHONY: \
	help
