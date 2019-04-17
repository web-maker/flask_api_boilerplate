#!/usr/bin/env bash

cd "$(pwd)"

if [[ ! -w "." ]]; then
    echo "You don't have rights to write in current directory"
    exit 1
fi

PYTHON_OK=`python3 -c 'import sys
print (sys.version_info >= (3, 6, 3) and "1" or "0")'`

if [[ "$PYTHON_OK" == '0' ]]; then
    echo "Python version must be 3.6.3 or higher"
    exit 1
fi

if [[ ! -d "env" ]]; then
    mkdir env
fi

python3 -m venv env/ && source ../env/bin/activate
echo "Created virtual environment"

echo "Installing requirements"
pip install -r requirements.txt
echo "Requirements already installed"

flake8 --install-hook git
git config --bool flake8.strict true

if [[ ! -f ".env" ]]; then
    cp .env.example .env
    echo ".env file was created"
fi

if [[ ! -f ".flaskenv" ]]; then
    cp .flaskenv.example .flaskenv
    echo ".flaskenv file was created"
fi
