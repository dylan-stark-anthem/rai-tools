# raitools: Tools for Responsible AI development

This repository hosts tools and utilities for working on AI responsibly.

Interested in contributing? Please check out the [contributing guidelines](CONTRIBUTING.md).

## Usage

See the [examples](examples/) for runnable samples for real (or realistic) scenarios.
For example, you can run the [UCI Adult Data Set](examples/data_drift/uci_adult/) example with

```
make -C examples/data_drift/uci_adult/data
python examples/data_drift/uci_adult/uci_adult.py
```

## Installation

```
pip install git+https://<user-id>@bitbucket.anthem.com/HCAD/repos/rai-tools.git
```
