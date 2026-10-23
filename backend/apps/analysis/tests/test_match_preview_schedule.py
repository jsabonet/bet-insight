from django.core.management import call_command
from django.test import TestCase
from django_celery_beat.models import PeriodicTask


class MatchPreviewScheduleTests(TestCase):
    def test_schedule_sync_is_idempotent(self):
        call_command('sync_match_preview_schedule')
        call_command('sync_match_preview_schedule')

        task = PeriodicTask.objects.get(name='precompute-match-previews')
        self.assertEqual(task.task, 'analysis.precompute_match_previews')
        self.assertTrue(task.enabled)
        self.assertEqual(task.crontab.hour, '5')
        self.assertEqual(task.crontab.minute, '0')
        self.assertEqual(task.crontab.timezone.key, 'UTC')
        self.assertEqual(PeriodicTask.objects.filter(name='precompute-match-previews').count(), 1)

        reminder_task = PeriodicTask.objects.get(name='send-analyzed-match-reminders')
        self.assertEqual(reminder_task.task, 'notifications.send_analyzed_match_reminders')
        self.assertTrue(reminder_task.enabled)
        self.assertEqual(reminder_task.crontab.minute, '*/5')
        self.assertEqual(reminder_task.crontab.timezone.key, 'UTC')
        self.assertEqual(PeriodicTask.objects.filter(name='send-analyzed-match-reminders').count(), 1)
