import django
import pydoc
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'abv.settings'
django.setup()
pydoc.cli()
