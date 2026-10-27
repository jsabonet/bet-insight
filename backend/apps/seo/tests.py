from django.test import RequestFactory, SimpleTestCase, override_settings

from .sitemaps import StaticViewSitemap
from .views import robots_txt


class PublicSitemapTests(SimpleTestCase):
    def test_sitemap_contains_only_existing_public_frontend_pages(self):
        sitemap = StaticViewSitemap()

        self.assertEqual(
            [sitemap.location(item) for item in sitemap.items()],
            ['/', '/about', '/faq', '/terms', '/privacy', '/affiliate/terms'],
        )


class RobotsTxtTests(SimpleTestCase):
    @override_settings(FRONTEND_URL='https://placarcerto.digital/')
    def test_robots_txt_points_to_canonical_sitemap_and_excludes_private_routes(self):
        response = robots_txt(RequestFactory().get('/robots.txt'))
        content = response.content.decode()

        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('Sitemap: https://placarcerto.digital/sitemap.xml', content)
        self.assertIn('Disallow: /api/', content)
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Disallow: /home', content)
