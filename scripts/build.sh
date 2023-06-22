#!/bin/bash

cd /workspace/email-processor/app

apt-get install python3-venv -y &> /dev/null

python3 -m venv v-env &> /dev/null

source v-env/bin/activate &> /dev/null

pip install --upgrade pip &> /dev/null

pip install -r requirements.txt &> /dev/null