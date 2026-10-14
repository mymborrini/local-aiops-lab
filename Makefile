.PHONY: install run-app docker-up docker-down traffic-generator

install:
	pip install -e ".[dev]"

run-app:
	uvicorn app.main.fast_api_app:app --reload

docker-up:
	docker compose up --build job_processor -d 

docker-down:
	docker compose down

traffic-generator:
	py traffic_generator.py 8000 --interval 10
