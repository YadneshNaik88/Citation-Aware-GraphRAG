# Makefile for Citation-Aware-GraphRAG
# Protocol and Architecture: Architecture B v1.1

ifeq ($(OS),Windows_NT)
    VENV_DIR := .venv
    VENV_PYTHON := $(VENV_DIR)\Scripts\python.exe
    SYSTEM_PYTHON ?= py -3.13
else
    VENV_DIR := .venv
    VENV_PYTHON := $(VENV_DIR)/bin/python
    SYSTEM_PYTHON ?= python3
endif

.PHONY: all setup test lint leakage lock env-report clean

all: lint test

setup:
	$(SYSTEM_PYTHON) -m venv $(VENV_DIR)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements-lock.txt

test:
	$(VENV_PYTHON) -m pytest tests

lint:
	$(VENV_PYTHON) -m ruff check .
	$(VENV_PYTHON) -m ruff format --check .

leakage:
	@$(SYSTEM_PYTHON) -c "print('Leakage audit skeleton placeholder (to be implemented in T0.4)')"

lock:
	$(SYSTEM_PYTHON) -c "import shutil; shutil.rmtree('.venv_lock', ignore_errors=True)"
	$(SYSTEM_PYTHON) -m venv .venv_lock
ifeq ($(OS),Windows_NT)
	.venv_lock\Scripts\python.exe -m pip install --upgrade pip
	.venv_lock\Scripts\python.exe -m pip install -r requirements.txt
	.venv_lock\Scripts\python.exe -m pip freeze > requirements-lock.txt
else
	.venv_lock/bin/python -m pip install --upgrade pip
	.venv_lock/bin/python -m pip install -r requirements.txt
	.venv_lock/bin/python -m pip freeze > requirements-lock.txt
endif
	$(SYSTEM_PYTHON) -c "import shutil; shutil.rmtree('.venv_lock', ignore_errors=True)"

env-report:
	$(VENV_PYTHON) scripts/env_report.py

clean:
	$(SYSTEM_PYTHON) -c "import shutil; shutil.rmtree('.pytest_cache', ignore_errors=True); shutil.rmtree('.ruff_cache', ignore_errors=True)"
