"""
Configuração personalizada do Django Admin para PlacerCerto
"""
from django.contrib import admin
from django.http import HttpResponseRedirect
from urllib.parse import urlencode


class PlacerCertoAdminSite(admin.AdminSite):
    """
    Custom Admin Site para PlacerCerto.digital
    """
    site_header = "PlacerCerto Admin"
    site_title = "PlacerCerto"
    index_title = "Painel Administrativo"
    site_url = "https://placarcerto.digital"

    def login(self, request, extra_context=None):
        next_path = request.GET.get('next') or request.POST.get('next', '')
        if (
            not next_path.startswith('/admin/')
            or next_path.startswith('//')
            or '\\' in next_path
        ):
            next_path = '/admin/'
        return HttpResponseRedirect(f'/login?{urlencode({"next": next_path})}')
    
    def each_context(self, request):
        """
        Adiciona contexto personalizado a todas as páginas do admin
        """
        context = super().each_context(request)
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        context['site_url'] = self.site_url
        return context


# Instância do admin personalizado
admin_site = PlacerCertoAdminSite(name='placercerto_admin')
