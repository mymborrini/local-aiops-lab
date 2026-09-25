.PHONY: install run-app docker-up

install:
	pip install -e ".[dev]"

run-app:
	uvicorn app.main.app:app --reload

docker-up:
	docker compose up --build worker --build app -d