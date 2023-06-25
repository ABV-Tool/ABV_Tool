from django.contrib import admin
from .models import Antrag, Sitzung, Referat, Antragssteller, Antragstyp, Beschluss, Anlage

class AntragAdmin(admin.ModelAdmin):
    """Register your models here."""
    list_display = ('antragTitel', 'get_antragstyp', 'get_referat', 'get_sitzung_date', 'get_antragsteller', 'get_beschluss')
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
        return obj.astellerID.astellerName
    @admin.display(description='Beschluss')
    def get_beschluss(self, obj):
        if obj.beschlussID == None:
            return "Offen"
        else:
            return obj.beschlussID.beschlussErgebnis
admin.site.register(Antrag, AntragAdmin)


class SitzungAdmin(admin.ModelAdmin):
    """https://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field"""
    list_display = ('sitzID', 'get_referat', 'sitzDate', 'sitzNummerJahr')
    ordering=('sitzDate', 'refID')
    @admin.display(description='Referat')
    def get_referat(self, obj):
        return obj.refID.refName
admin.site.register(Sitzung, SitzungAdmin)


class ReferatAdmin(admin.ModelAdmin):
    list_display = ('refID','refName', 'refEmail')
    ordering = ('refID',)
admin.site.register(Referat, ReferatAdmin)


class AntragstypAdmin(admin.ModelAdmin):
    list_display = ('typID', 'typName', 'typSlug')
    ordering = ('typID',)
admin.site.register(Antragstyp, AntragstypAdmin)


class AntragsstellerAdmin(admin.ModelAdmin):
    list_display = ('astellerID', 'astellerName')
admin.site.register(Antragssteller, AntragsstellerAdmin)


class BeschlussAdmin(admin.ModelAdmin):
    list_display = ('sitzID', 'beschlussDate', 'beschlussFaehigkeit', 'get_ergebnis')
admin.site.register(Beschluss, BeschlussAdmin)


class AnlageAdmin(admin.ModelAdmin):
    list_display = ('anlage', 'antragID')
admin.site.register(Anlage, AnlageAdmin)


