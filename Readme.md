# Local AIOPS lab

## Requirements

### Python

You need python version 3.12
1. Install it for your operating system 
2. setup virtualenv

    py -3.12 -m venv myvenv

3. Activate it, for example in Windows

    .\myvenv\Scripts\Activate.ps1

### Build the project

    make install

### Swagger

    http://localhost:8000/docs

### Commands

#### Redis

Check the keys in the queue:

    docker compose exec redis redis-cli
    LRANGE jobs 0 -1