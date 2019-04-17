#!/bin/bash
set -e

# go to project root directory and activate env
cd "$(pwd)"
source env/bin/activate

# install requirements
pip install -r requirements.txt

# check PEP8
flake8 .

# upgrade DB
flask db upgrade

# restart process
pm2 stop pm2.config.js
pm2 start pm2.config.js

echo "Server was successfully restarted"
