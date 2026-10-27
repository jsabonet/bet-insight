"""
Views para SEO - robots.txt e outras configurações
"""
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    """
    Arquivo robots.txt otimizado para SEO
    """
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Disallow: /home",
        "Disallow: /daily-bets",
        "Disallow: /match/",
        "Disallow: /my-analyses",
        "Disallow: /profile",
        "",
        "# Sitemaps",
        f"Sitemap: {settings.FRONTEND_URL.rstrip('/')}/sitemap.xml",
    ]
    
    return HttpResponse("\n".join(lines), content_type="text/plain")
