from datetime import datetime, date, time
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext

from models import HorarioSolicitacao, Solicitacao
from forms import SolicitacaoAddForm

def solicitacao_add_view(request, form_url='', extra_context=None):
    horarios = HorarioSolicitacao.objects.all()
    horario_atual = None
    permitido = False
    for horario in horarios:
        agora = datetime.time(datetime.now())
        if agora > horario.hora_inicio and agora < horario.hora_fim:
            horario_atual = horario
            permitido = True
            break
    if request.user.is_superuser:
        permitido = True
    if permitido == False:
        context = {"permitido": False, "horarios": horarios}
        context.update(extra_context or {})
        return render_to_response("solicitacao_nao_permitido.html", context, context_instance=RequestContext(request))

    if horario_atual is not None:
        datahora_inicio = datetime.combine(datetime.today(), horario_atual.hora_inicio)
        datahora_fim = datetime.combine(datetime.today(), horario_atual.hora_fim)
        qs = Solicitacao.objects.filter(aluno=request.user, data__lt=datahora_fim, data__gt=datahora_inicio)
        if qs.count() > 0:
            context = extra_context or {}
            return render_to_response("solicitacao_resposta.html", context, context_instance=RequestContext(request))
    
    form = SolicitacaoAddForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.aluno = request.user
            inscricao.save()
            context = extra_context or {}
            return render_to_response("solicitacao_resposta.html", context, context_instance=RequestContext(request))
    else:
        form = SolicitacaoAddForm()
        context = {"form": form, "permitido": True}
        context.update(extra_context or {})
        return render_to_response("solicitacao_form.html", context, context_instance=RequestContext(request))
