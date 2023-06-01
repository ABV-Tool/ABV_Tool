# Database uuid
http://www.seanbehan.com/how-to-enable-uuids-in-postgres/


# Django Login

## Erstellung eines Superusers

[Verwendeter Guide](https://learndjango.com/tutorials/django-login-and-logout-tutorial)

=> `python manage.py createsuperuser`

Credentials:
* Login:    abv
* Email:    abv@stura.htw-dresden.de
* PW:       J9AHJL4hD3vc2PwP


# Docker-Compose Setup
Guide: https://github.com/docker/awesome-compose/blob/master/official-documentation-samples/django/README.md

## Probleme

### Django-JSONField Error:

#### Fehlermeldung

```
src-web-1  |   File "/usr/local/lib/python3.11/site-packages/jsonfield/__init__.py", line 3, in <module>
src-web-1  |     from .fields import JSONField
src-web-1  |   File "/usr/local/lib/python3.11/site-packages/jsonfield/fields.py", line 9, in <module>
src-web-1  |     from django.utils.translation import ugettext_lazy as _
src-web-1  | ImportError: cannot import name 'ugettext_lazy' from 'django.utils.translation' (/usr/local/lib/python3.11/site-packages/django/utils/translation/__init
```

#### Voraussichtlich permanenter Fix:
https://forum.djangoproject.com/t/importerror-cannot-import-name-ugettext-lazy-from-django-utils-translation/10943/10

#### Temporärer Fix:
https://forum.djangoproject.com/t/importerror-cannot-import-name-ugettext-lazy-from-django-utils-translation/10943/4
=> Ausführung in lokalem `venv`

# TailwindCSS Setup

Guide: https://django-tailwind.readthedocs.io/en/latest/installation.html

Problem: Abhängigkeit von NPM => NPM-Pfad muss gesetzt werden

## Start

`python manage.py tailwind start`

## Build

`python manage.py tailwind build`