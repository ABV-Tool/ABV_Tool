#!/bin/sh

python3 abv/manage.py makemigrations
python3 abv/manage.py migrate

python3 abv/manage.py loaddata abv/Antragstool/fixtures/referate.json
python3 abv/manage.py loaddata abv/Antragstool/fixtures/sitzungen.json
python3 abv/manage.py loaddata abv/Antragstool/fixtures/antragstyp.json
