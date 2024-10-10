#!/bin/bash
#pipenv shell

poetry shell
poetry install

case $1 in
  dev)
    poetry run  python manage.py runserver --settings=main.settings.dev
    ;;
#  prod)
#    poetry run  python manage.py collectstatic --noinput
#    poetry run  python manage.py makemigrations
#    poetry run  python manage.py migrate
#    poetry run  python manage.py runserver --settings=main.settings.prod
#    ;;
esac
