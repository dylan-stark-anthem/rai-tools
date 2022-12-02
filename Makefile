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

lint:
	poetry run flake8 src tests

test:
	poetry run pytest -x --cov

type_check:
	poetry run mypy src tests --ignore-missing-import

accept:
	poetry run behave --stop

accept_wip:
	poetry run behave --stop --tags=wip

################################################################################

examples:
	poetry run python examples/data_drift/uci_adult/uci_adult.py

################################################################################

.PHONY: \
	accept \
	accept_wip \
	build \
	examples
	help \
	lint \
	setup \
	test \
	type_check
