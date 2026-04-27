SHELL := /bin/bash
export PYTHONPATH := $(CURDIR)

.PHONY: dev up down test lint install format

install:
	pip install -e ".[dev]"

dev:
	uvicorn src.jarvis.api.main:app --reload --host 0.0.0.0 --port 8000

up:
	docker compose up --build -d

down:
	docker compose down

test:
	pytest tests/ -v

lint:
	ruff check src/ cli/ tests/
	ruff format --check src/ cli/ tests/

format:
	ruff check --fix src/ cli/ tests/
	ruff format src/ cli/ tests/
