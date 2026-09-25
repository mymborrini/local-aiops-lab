.PHONY: install freeze dev run-app

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

dev:
	pip install -e .

run-app:
	uvicorn app.main.app:app --reload