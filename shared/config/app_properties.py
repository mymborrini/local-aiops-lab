import os

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "jobs")
POSTGRES_USER = os.getenv("POSTGRES_USER", "jobs")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "jobs")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))

LOKI_URL = os.getenv("LOKI_URL", None) 
SERVICE_NAME = os.getenv("SERVICE_NAME", "app")