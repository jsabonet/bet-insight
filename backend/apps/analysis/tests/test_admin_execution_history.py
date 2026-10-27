from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.analysis.models import TaskExecution
from apps.users.models import User


class AdminExecutionHistoryTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='history_admin',
            email='history_admin@example.com',
            password='test-password',
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin)
        now = timezone.now()
        self.generation = TaskExecution.objects.create(
            task_name='generate_daily_bets',
            task_id='history-generation',
            status='success',
            triggered_by='manual',
            triggered_by_user=self.admin,
        )
        self.validation = TaskExecution.objects.create(
            task_name='validate_daily_bets',
            task_id='history-validation',
            status='failed',
            triggered_by='celery',
            error_message='Falha temporária de validação',
        )
        TaskExecution.objects.filter(pk=self.generation.pk).update(
            started_at=now - timedelta(days=5),
        )
        TaskExecution.objects.filter(pk=self.validation.pk).update(
            started_at=now - timedelta(days=1),
        )

    def test_execution_history_filters_by_task_status_date_and_search(self):
        response = self.client.get(
            '/api/daily-bets/admin/execution-status/',
            {
                'task_name': 'validate_daily_bets',
                'status': 'failed',
                'date_from': (timezone.localdate() - timedelta(days=2)).isoformat(),
                'date_to': timezone.localdate().isoformat(),
                'search': 'temporária',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['executions']], [self.validation.id])
        self.assertEqual(response.data['pagination']['total'], 1)

    def test_execution_history_paginates_results(self):
        response = self.client.get(
            '/api/daily-bets/admin/execution-status/',
            {'page': 2, 'page_size': 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['executions']), 1)
        self.assertEqual(response.data['pagination']['page'], 2)
        self.assertEqual(response.data['pagination']['total'], 2)
        self.assertEqual(response.data['pagination']['total_pages'], 2)

    def test_execution_history_rejects_reversed_date_range(self):
        response = self.client.get(
            '/api/daily-bets/admin/execution-status/',
            {
                'date_from': timezone.localdate().isoformat(),
                'date_to': (timezone.localdate() - timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 400)
