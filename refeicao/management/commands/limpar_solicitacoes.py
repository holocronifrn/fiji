# -*- coding: utf-8 -*-
from datetime import datetime, date, time
from django.core.management.base import NoArgsCommand
from refeicao.models import Solicitacao, HorarioSolicitacao

class Command(NoArgsCommand):
    help = "Limpar registros de solicitação bolsa refeição"
    def handle_noargs(self, **options):
        horarios = HorarioSolicitacao.objects.filter(hora_inicio__lt=datetime.now()).order_by("hora_fim")
        horario = horarios[0]
        datahora_inicio = datetime.combine(datetime.today(), horario.hora_inicio)
        Solicitacao.objects.filter(data__lt=datahora_inicio).delete()
        self.stdout.write("Todos os itens foram removidos.\n")