# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.conf import settings

class ButtonAdmin(admin.ModelAdmin):
    """
    A subclass of this admin will let you add buttons (like history) in the
    change view of an entry.

    ex.
    class FooAdmin(ButtonAdmin):
       ...

       def bar(self, request, obj=None):
          if obj != None: obj.bar()
          return None # Redirect or Response or None
       bar.short_description='Example button'

       list_buttons = [ bar ]
       change_buttons = [ bar ]

    you can then put the following in your admin/change_form.html template:

       {% block object-tools %}
           {% if change %}{% if not is_popup %}
           <ul class="object-tools">
           {% for button in buttons %}
             <li><a href="{{ button.func_name }}/">{{ button.short_description }}</a></li>
           {% endfor %}
           <li><a href="history/" class="historylink">History</a></li>
           {% if has_absolute_url %}<li><a href="../../../r/{{ content_type_id }}/{{ object_id }}/" class="viewsitelink">View on site</a></li>{% endif%}
           </ul>
           {% endif %}{% endif %}
       {% endblock %}

    """
    change_buttons=[]
    list_buttons=[]

    def button_view_dispatcher(self, request, url):
        # Dispatch the url to a function call
        if url is not None:
            import re
            res = re.match('(.*/)?(?P<id>\d+)/(?P<command>.*)', url)
            if res:
                if res.group('command') in [b.func_name for b in self.change_buttons]:
                    obj = self.model._default_manager.get(pk=res.group('id'))
                    response = getattr(self, res.group('command'))(request, obj)
                    if response is None:
                        from django.http import HttpResponseRedirect
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    return response
            else:
                res = re.match('(.*/)?(?P<command>.*)', url)
                if res:
                    if res.group('command') in [b.func_name for b in self.list_buttons]:
                        response = getattr(self, res.group('command'))(request)
                        if response is None:
                            from django.http import HttpResponseRedirect
                            return HttpResponseRedirect(request.META['HTTP_REFERER'])
                        return response
        # Delegate to the appropriate method, based on the URL.
        from django.contrib.admin.util import unquote
        if url is None:
            return self.changelist_view(request)
        elif url == "add":
            return self.add_view(request)
        elif url.endswith('/history'):
            return self.history_view(request, unquote(url[:-8]))
        elif url.endswith('/delete'):
            return self.delete_view(request, unquote(url[:-7]))
        else:
            return self.change_view(request, unquote(url))

    def get_urls(self):
        from django.conf.urls.defaults import url, patterns
        from django.utils.functional import update_wrapper
        # Define a wrapper view
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        #  Add the custom button url
        urlpatterns = patterns('',
            url(r'^(.+)/$', wrap(self.button_view_dispatcher),)
        )
        return urlpatterns + super(ButtonAdmin, self).get_urls()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not extra_context: extra_context = {}
        if hasattr(self, 'change_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.change_buttons)
            self.change_form_template = "admin/change_form_with_buttons.html"
        if '/' in object_id:
            object_id = object_id[:object_id.find('/')]
        return super(ButtonAdmin, self).change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=[]):
        if not extra_context: extra_context = {}
        if hasattr(self, 'list_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.list_buttons)
        if hasattr(self, 'string_overrides'):
            if 'changelist_title' in self.string_overrides and 'title' not in extra_context:
                extra_context['title'] = self.string_overrides['changelist_title']
        return super(ButtonAdmin, self).changelist_view(request, extra_context)

    def _convert_buttons(self, orig_buttons):
        buttons = []
        for b in orig_buttons:
            buttons.append({ 'func_name': b.func_name, 'short_description': b.short_description })
        return buttons

class ModelAdminPlus(ButtonAdmin):
    def set_readonly(self, request):
        request.readonly = True

    def has_view_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(u"%s.view_%s" %
            (self.model._meta.app_label, self.model._meta.object_name.lower()))

    def has_change_permission(self, request, obj=None):
        has_perm = super(ModelAdminPlus, self).has_change_permission(request, obj)
        if not has_perm and self.has_view_permission(request, obj):
            self.set_readonly(request)
            return True
        else:
            return has_perm
            
    def changelist_view(self, request, extra_context=None):
        try:
            return super(ModelAdminPlus, self).changelist_view(
                request, extra_context=extra_context)
        except PermissionDenied:
            if not self.has_view_permission(request):
                raise PermissionDenied
        if request.method == 'POST':
            raise PermissionDenied
        if not getattr(request, 'readonly', False):
            self.set_readonly(request)
        return super(ModelAdminPlus, self).changelist_view(
            request, extra_context=extra_context)
                
    def change_view(self, request, object_id, extra_context=None):
        try:
            return super(ModelAdminPlus, self).change_view(
                request, object_id, extra_context=extra_context)
        except PermissionDenied:
            if not self.has_view_permission(request):
                raise PermissionDenied
        if request.method == 'POST':
            raise PermissionDenied
        if not getattr(request, 'readonly', False):
            self.set_readonly(request)
        return super(ModelAdminPlus, self).change_view(
            request, object_id, extra_context=extra_context)
    
    def get_actions(self, request):
        actions = super(ModelAdminPlus, self).get_actions(request)
        if not self.has_delete_permission(request) and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, obj=None):
        if getattr(request, 'readonly', False):
            return list([f.name for f in self.model._meta.fields])
        else:
            return super(ModelAdminPlus, self).get_readonly_fields(request, obj)

class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        if request.user.groups.filter(name="Alunos").count() > 0:
            return HttpResponseRedirect(reverse("admin:refeicao_solicitacao_add"))
        elif request.user.has_perm("refeicao.change_solicitacao"):
            return HttpResponseRedirect(reverse("admin:refeicao_solicitacao_changelist"))
        else:
            return super(CustomAdminSite, self).index(request, extra_context)

admin.site = CustomAdminSite()
