"""
Views para SEO - robots.txt e outras configurações
"""
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
        "Disallow: /my-analyses/",
        "Disallow: /profile/",
        "",
        "# Sitemaps",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
        "",
        "# Crawl-delay para bots agressivos",
        "User-agent: *",
        "Crawl-delay: 1",
        "",
        "# Bots específicos otimizados",
        "User-agent: Googlebot",
        "Allow: /",
        "Crawl-delay: 0",
        "",
        "User-agent: Bingbot",
        "Allow: /",
        "Crawl-delay: 0",
        "",
        "# Bloquear bots indesejados",
        "User-agent: AhrefsBot",
        "Disallow: /",
        "",
        "User-agent: SemrushBot",
        "Disallow: /",
        "",
        "User-agent: MJ12bot",
        "Disallow: /",
    ]
    
    return HttpResponse("\n".join(lines), content_type="text/plain")
