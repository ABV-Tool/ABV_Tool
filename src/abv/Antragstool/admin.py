from django.contrib import admin
from .models import Antrag, Sitzung, Referat, Antragssteller, Antragstyp

# Register your models here.
class AntragAdmin(admin.ModelAdmin):
    list_display = ('antragTitel', 'get_antragstyp', 'get_referat', 'get_sitzung_date', 'get_antragsteller', )
    @admin.display(description='Referat')
    def get_referat(self, obj):
        return obj.sitzID.refID.refName
    @admin.display(description='Sitzungsdatum')
    def get_sitzung_date(self, obj):
        return obj.sitzID.sitzDate
    @admin.display(description='Antragstyp')
    def get_antragstyp(self, obj):
        return obj.typID.typName
    @admin.display(description='Antragsteller')
    def get_antragsteller(self, obj):
        return obj.astellerID.astellerVorname + ' ' + obj.astellerID.astellerName
admin.site.register(Antrag, AntragAdmin)


# https://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field
class SitzungAdmin(admin.ModelAdmin):
    list_display = ('sitzID', 'get_referat', 'sitzDate')
    ordering=('sitzDate', 'refID')
    @admin.display(description='Referat')
    def get_referat(self, obj):
        return obj.refID.refName
admin.site.register(Sitzung, SitzungAdmin)


class ReferatAdmin(admin.ModelAdmin):
    list_display = ('refID','refName', 'refZyklus')
    ordering = ('refID',)
admin.site.register(Referat, ReferatAdmin)


class AntragstypAdmin(admin.ModelAdmin):
    list_display = ('typID', 'typName', 'typSlug')
    ordering = ('typID',)
admin.site.register(Antragstyp, AntragstypAdmin)


class AntragsstellerAdmin(admin.ModelAdmin):
    list_display = ('astellerID', 'astellerName', 'astellerVorname')
admin.site.register(Antragssteller, AntragsstellerAdmin)
