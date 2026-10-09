.PHONY: install run-app docker-up docker-down

install:
	pip install -e ".[dev]"

run-app:
	uvicorn app.main.fast_api_app:app --reload

docker-up:
	docker compose up --build app --build job_processor --build outbox_processor --build prometheus -d

docker-down:
	docker compose down
