help:
	cat Makefile

################################################################################

setup:
	pre-commit install --install-hooks
	poetry install

build:
	poetry install
	poetry run black src tests
	poetry run flake8 src tests
	poetry run mypy src tests --ignore-missing-import
	poetry run pytest --cov

test:
	poetry run pytest --cov

type_check:
	poetry run mypy src tests --ignore-missing-import

################################################################################

.PHONY: \
	build \
	help \
	setup \
	test
