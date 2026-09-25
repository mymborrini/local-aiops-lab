# Local AIOPS lab

## Requirements

### Python

You need python version 3.12
1. Install it for your operating system 
2. setup virtualenv

    py -3.12 -m venv myvenv

3. Activate it, for example in Windows

    .\myvenv\Scripts\Activate.ps1

### Install dependecies

After you set up the python virtual environment, install dependencies

    pip install -r requirements.txt

### Build the project

    pip install -e .

### Swagger

    http://localhost:8000/docs