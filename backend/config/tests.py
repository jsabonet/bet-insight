from django.test import SimpleTestCase


class AdminLoginRedirectTests(SimpleTestCase):
    def test_admin_login_redirects_to_application_login_and_preserves_admin_path(self):
        response = self.client.get('/admin/login/?next=/admin/users')

        self.assertRedirects(
            response,
            '/login?next=%2Fadmin%2Fusers',
            fetch_redirect_response=False,
        )

    def test_admin_login_rejects_external_redirect_targets(self):
        response = self.client.get('/admin/login/?next=https://example.com')

        self.assertRedirects(
            response,
            '/login?next=%2Fadmin%2F',
            fetch_redirect_response=False,
        )
