PY = .venv/bin/python

.PHONY: install run test lint up down

install:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

run:
	PYTHONPATH=src $(PY) -m pipeline.run --layer all

test:
	PYTHONPATH=src $(PY) -m pytest -v

lint:
	$(PY) -m ruff check .

up:
	mkdir -p data && chmod -R 777 data
	docker compose up -d

down:
	docker compose down
