import autocomplete_light
from django.contrib.auth.models import User

autocomplete_light.register(User,
    search_fields=['^first_name', 'last_name', 'username'],
    autocomplete_js_attributes={'placeholder': 'aluno...'}
)