from django.contrib import admin
from .models import Antrag, Sitzung, Referat, Antragssteller, Antragstyp

# Register your models here.
admin.site.register(Antrag)
admin.site.register(Sitzung)
admin.site.register(Referat)
admin.site.register(Antragstyp)
admin.site.register(Antragssteller)
