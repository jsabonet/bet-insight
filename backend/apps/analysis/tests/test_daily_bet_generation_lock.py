from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase

from apps.analysis.models import TaskExecution
from apps.analysis.tasks import generate_daily_bets
from apps.analysis.services.daily_bet_generation_lock import (
    GENERATION_LOCK_KEY,
    acquire_generation_lock,
    get_generation_lock_owner,
    release_generation_lock,
    renew_generation_lock,
)


class DailyBetGenerationLockTests(SimpleTestCase):
    def setUp(self):
        cache.delete(GENERATION_LOCK_KEY)

    def tearDown(self):
        cache.delete(GENERATION_LOCK_KEY)

    def test_only_one_owner_can_claim_and_release_lock(self):
        self.assertTrue(acquire_generation_lock('task-one'))
        self.assertFalse(acquire_generation_lock('task-two'))
        self.assertEqual(get_generation_lock_owner(), 'task-one')
        self.assertTrue(renew_generation_lock('task-one'))
        self.assertFalse(renew_generation_lock('task-two'))

        release_generation_lock('task-two')
        self.assertEqual(get_generation_lock_owner(), 'task-one')

        release_generation_lock('task-one')
        self.assertTrue(acquire_generation_lock('task-two'))


class GenerateDailyBetsTaskLockTests(TestCase):
    def setUp(self):
        cache.delete(GENERATION_LOCK_KEY)

    def tearDown(self):
        cache.delete(GENERATION_LOCK_KEY)

    @patch('apps.analysis.services.daily_bet_generator.DailyBetGenerator')
    def test_manual_task_reuses_execution_created_by_request(self, generator_class):
        task_id = 'manual-generation-task'
        execution = TaskExecution.objects.create(
            task_name='generate_daily_bets',
            task_id=task_id,
            triggered_by='manual',
        )
        self.assertTrue(acquire_generation_lock(task_id))
        generator_class.return_value.generate_for_today.return_value = {
            'total_bets': 0,
            'multiple_count': 0,
            'value_count': 0,
            'matches_analyzed': 0,
            'api_calls': 0,
        }

        result = generate_daily_bets.apply(
            kwargs={'triggered_by': 'manual', 'mode': 'hybrid'},
            task_id=task_id,
        ).get()

        execution.refresh_from_db()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(
            TaskExecution.objects.filter(task_id=task_id).count(),
            1,
        )
        self.assertEqual(execution.status, 'success')
        generator_class.return_value.generate_for_today.assert_called_once_with(
            mode='hybrid',
            execution=execution,
        )
        self.assertIsNone(get_generation_lock_owner())

    @patch('apps.analysis.services.daily_bet_generator.DailyBetGenerator')
    def test_task_skips_when_another_generation_owns_the_lock(self, generator_class):
        self.assertTrue(acquire_generation_lock('active-generation'))

        result = generate_daily_bets.apply(
            kwargs={'triggered_by': 'celery'},
            task_id='scheduled-generation',
        ).get()

        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'generation_already_running')
        generator_class.assert_not_called()
        self.assertEqual(TaskExecution.objects.count(), 0)

    @patch('apps.analysis.services.daily_bet_generator.DailyBetGenerator')
    def test_scheduled_task_still_runs_with_celery_trigger(self, generator_class):
        generator_class.return_value.generate_for_today.return_value = {
            'total_bets': 0,
            'multiple_count': 0,
            'value_count': 0,
            'matches_analyzed': 0,
            'api_calls': 0,
        }

        result = generate_daily_bets.apply(
            kwargs={},
            task_id='scheduled-generation-task',
        ).get()

        execution = TaskExecution.objects.get(task_id='scheduled-generation-task')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(execution.triggered_by, 'celery')
        generator_class.return_value.generate_for_today.assert_called_once_with(
            mode='hybrid',
            execution=execution,
        )