.PHONY: install run-app docker-up docker-down

install:
	pip install -e ".[dev]"

run-app:
	uvicorn app.main.app:app --reload

docker-up:
	docker compose up --build app --build job-processor --build outbox-processor -d

docker-down:
	docker compose down
