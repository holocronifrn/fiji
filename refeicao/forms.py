from django.forms.models import ModelForm
from models import Solicitacao

class SolicitacaoAddForm(ModelForm):
	class Meta:
		model = Solicitacao
		fields = ("motivo",)
