FROM python:3.12-slim

WORKDIR /app
WORKDIR /shared

COPY app ./app
COPY shared ./shared
COPY pyproject.toml .

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "app.main.app:app", "--host", "0.0.0.0", "--port", "8000"]
