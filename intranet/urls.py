from django.conf.urls import patterns, include, url
import intranet.admin

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)
