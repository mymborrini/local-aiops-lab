.PHONY: install run-app docker-up docker-down traffic-generator heavy-load-generator

install:
	pip install -e ".[dev]"

run-app:
	uvicorn app.main.fast_api_app:app --reload

docker-up:
	docker compose up --build grafana -d

docker-down:
	docker compose down

traffic-generator:
	py tests_scripts/traffic_generator.py 8000 --interval 10

heavy-load-generator:
	py tests_scripts/heavy_load_generator.py 8000 --request 100 --concurrency 5
