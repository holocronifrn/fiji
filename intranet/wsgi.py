import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intranet.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "intranet.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
