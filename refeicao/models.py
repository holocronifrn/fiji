# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import auth
from intranet.models import ModelPlus
from django.contrib.auth.models import User

dias_da_semana_choices = ((0, "Segunda-feira"), (1, "Terça-feira"), (2, "Quarta-feira"), (3, "Quinta-feira"), (4, "Sexta-feira"))
tipos_de_refeicao_choices = ((1, "Almoço"), (2, "Jantar"))

def get_full_name(self):
    return "%s %s" % (self.first_name, self.last_name)

User.full_name = property(get_full_name)
User.__unicode__ = lambda self: "%s - %s %s" % (self.username, self.first_name, self.last_name)

class HorarioSolicitacao(models.Model):
    hora_inicio = models.TimeField()
    hora_inicio.verbose_name = "da (hora)"
    hora_fim = models.TimeField()
    hora_fim.verbose_name = "até (hora)"
    tipo = models.IntegerField(choices=tipos_de_refeicao_choices)
    class Meta:
        verbose_name = u"horario de solicitação"
        verbose_name_plural = u"horarios de solicitação"
        ordering = ["hora_inicio", "hora_fim"]

    def __str__(self):
        return "%s à %s" % (self.hora_inicio, self.hora_fim)

class Solicitacao(ModelPlus):
    aluno = models.ForeignKey(auth.models.User)
    aluno_nome = models.CharField(max_length=100)
    #tipo = models.IntegerField(choices=tipos_de_refeicao_choices)
    motivo = models.TextField()
    motivo.verbose_name = u"Motivo pelo qual necessita da refeição"
    data = models.DateTimeField(auto_now_add=True)
    aceito = models.BooleanField(default=0)

    class Meta(ModelPlus.Meta):
        verbose_name = u"solicitação de refeição"
        verbose_name_plural = u"solicitações de refeição"
        ordering = ["data", "aluno_nome"]

    def save(self):
        super(Solicitacao, self).save()
        self.aluno_nome = self.aluno.first_name + " " + self.aluno.last_name
        self.matricula = self.aluno.username
        super(Solicitacao, self).save()

    def __unicode__(self):
        return self.aluno_nome
