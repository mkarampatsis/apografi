#!/bin/bash
rsync -avz --delete .env models connection.py sdad*.py psped*.py utils.py requirements.txt lola:apografi
ssh lola 'source ~/apografi/venv/bin/activate && pip install -r ~/apografi/requirements.txt'
