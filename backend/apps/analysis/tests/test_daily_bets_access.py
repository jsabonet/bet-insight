from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

class DailyBetPremiumAccessTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='daily-bets-user',
            email='daily-bets@example.com',
            password='Strong-test-pass-123',
        )
        self.client.force_authenticate(self.user)

    def test_free_user_cannot_read_daily_selections_or_history(self):
        for endpoint in (
            '/api/daily-bets/today/',
            '/api/daily-bets/history/',
            '/api/daily-bets/',
            '/api/daily-bets/999999/',
        ):
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(response.status_code, 403)

    def test_expired_premium_user_cannot_read_daily_selections(self):
        self.user.is_premium = True
        self.user.premium_until = timezone.now() - timedelta(days=1)
        self.user.save(update_fields=['is_premium', 'premium_until'])

        response = self.client.get('/api/daily-bets/today/')

        self.assertEqual(response.status_code, 403)

    def test_active_premium_user_can_read_daily_selections(self):
        self.user.is_premium = True
        self.user.premium_until = timezone.now() + timedelta(days=1)
        self.user.save(update_fields=['is_premium', 'premium_until'])

        response = self.client.get('/api/daily-bets/today/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['multiple_tickets'], [])
        self.assertEqual(response.data['value_bets'], [])

    def test_admin_can_read_daily_selections(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        response = self.client.get('/api/daily-bets/today/')

        self.assertEqual(response.status_code, 200)

    def test_public_performance_stats_remain_available(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/daily-bets/stats/')

        self.assertEqual(response.status_code, 200)


class UserPremiumStatusSerializerTests(APITestCase):
    def test_profile_exposes_active_premium_status(self):
        user = get_user_model().objects.create_user(
            username='premium-status-user',
            email='premium-status@example.com',
            password='Strong-test-pass-123',
            is_premium=True,
            premium_until=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(user)

        response = self.client.get('/api/users/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_premium_active'])
