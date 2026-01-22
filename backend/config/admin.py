"""
Configuração personalizada do Django Admin para PlacerCerto
"""
from django.contrib import admin


class PlacerCertoAdminSite(admin.AdminSite):
    """
    Custom Admin Site para PlacerCerto.digital
    """
    site_header = "PlacerCerto Admin"
    site_title = "PlacerCerto"
    index_title = "Painel Administrativo"
    site_url = "https://placarcerto.digital"
    
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
