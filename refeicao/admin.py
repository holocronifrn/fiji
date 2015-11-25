# -*- coding: utf-8 -*-
from datetime import datetime, date, time
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
import autocomplete_light

from intranet.admin import ModelAdminPlus
from models import Solicitacao, HorarioSolicitacao, tipos_de_refeicao_choices
from forms import SolicitacaoAddForm
from views import solicitacao_add_view

class AdUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name")
    list_filter = []
    readonly_fields = ("first_name", "last_name")
    fieldsets = (
        (None, {'fields': ("first_name", "last_name", 'groups',)}),
    )
    def get_actions(self, request):
        actions = super(AdUserAdmin, self).get_actions(request)
        if actions.has_key("delete_selected"):
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

del UserAdmin.form

class SolicitacaoAdmin(ModelAdminPlus):
    readonly = True
    list_display = ("aluno_nome", "data", "motivo", "aceito")
    string_overrides = {
        "changelist_title": u"Solicitações de Refeição",
    }

    def __init__(self, *args, **kwargs):
        super(SolicitacaoAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def queryset(self, request):
        qs = super(SolicitacaoAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        horarios = HorarioSolicitacao.objects.filter(hora_inicio__lt=datetime.now()).order_by("-hora_fim")
        if(horarios.count() > 0):
            horario = horarios[0]
            datahora_inicio = datetime.combine(datetime.today(), horario.hora_inicio)
            datahora_fim = datetime.combine(datetime.today(), horario.hora_fim)
            return qs.filter(data__lt=datahora_fim, data__gt=datahora_inicio)

    def add_view(self, request, form_url='', extra_context=None):
        return solicitacao_add_view(request, form_url, extra_context)

    def deferir(self, request, queryset):
        for obj in queryset:
            obj.aceito = True
            obj.save()
        messages.info(request, "As incrições foram deferidas.")

    def indeferir(self, request, queryset):
        for obj in queryset:
            obj.aceito = False
            obj.save()
        messages.info(request, "As incrições foram indeferidas.")

    def limparRegistros(self, request, obj=None):
        for horario in HorarioSolicitacao.objects.all():
            agora = datetime.time(datetime.now())
            if agora > horario.hora_inicio and agora < horario.hora_fim:
                messages.warning(request, "Não permitido limpar registros durante o horário de solicitações.")
                return
        Solicitacao.objects.all().delete()
        messages.info(request, "Todos os itens foram removidos.")
    limparRegistros.short_description = "Limpar registros"

    def imprimirLista(self, request, obj=None):
        horarios = HorarioSolicitacao.objects.filter(hora_inicio__lt=datetime.now()).order_by("-hora_fim")
        if(horarios.count() > 0):
            horario = horarios[0]
            datahora_inicio = datetime.combine(datetime.today(), horario.hora_inicio)
            datahora_fim = datetime.combine(datetime.today(), horario.hora_fim)
            context = {
                "data": date.today(),
                "ficha": "Lista do %s" % (horario.get_tipo_display()),
                "alunos": [x.aluno for x in Solicitacao.objects.filter(aceito=True, data__lt=datahora_fim, data__gt=datahora_inicio)],
            }
            context["alunos"].sort(key=lambda x: x.full_name)
            return render_to_response("solicitacao_imprimir.html", context, context_instance=RequestContext(request))
    imprimirLista.short_description = "Imprimir lista"

    list_buttons = (imprimirLista,)
    actions = [deferir, indeferir]

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return super(SolicitacaoAdmin, self).has_change_permission(request, obj)
        else:
            return False

class HorarioSolicitacaoAdmin(ModelAdminPlus):
    list_display = ("tipo", "hora_inicio", "hora_fim")
    string_overrides = {
        "changelist_title": u"Horários de Solicitações",
    }

admin.site.unregister(User)
admin.site.register(User, AdUserAdmin)
admin.site.register(Solicitacao, SolicitacaoAdmin)
admin.site.register(HorarioSolicitacao, HorarioSolicitacaoAdmin)
