#!make

#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Custom variables
CMD := help

#* Custom shit
.PHONY: help
help: ## show this message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: requirements
requirements: ## build requirements file
#     @pip install pip-tools
	@PIP_PREFER_BINARY=1 pip-compile --quiet \
                        --output-file api/requirements/base.txt \
                        api/requirements/base.in
