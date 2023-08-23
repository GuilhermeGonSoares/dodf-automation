from django.contrib import admin
from .models import Unidade, Jurisdicionada

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'titular', 'email', 'ramal')

@admin.register(Jurisdicionada)
class JurisdicionadaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'coDemandante', 'sigla', 'unidade', 'apelido', 'vl_bens_serv', 'vl_obras_eng')
