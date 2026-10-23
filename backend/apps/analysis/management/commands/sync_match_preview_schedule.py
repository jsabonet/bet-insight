from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Garante os agendamentos periódicos de previews e lembretes push.'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='5',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='UTC',
        )
        PeriodicTask.objects.update_or_create(
            name='precompute-match-previews',
            defaults={
                'task': 'analysis.precompute_match_previews',
                'crontab': schedule,
                'interval': None,
                'solar': None,
                'clocked': None,
                'args': '[20]',
                'kwargs': '{}',
                'enabled': True,
                'description': 'Aquece o cache estatístico das próximas partidas às 05:00 UTC.',
            },
        )

        reminder_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='*/5',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='UTC',
        )
        PeriodicTask.objects.update_or_create(
            name='send-analyzed-match-reminders',
            defaults={
                'task': 'notifications.send_analyzed_match_reminders',
                'crontab': reminder_schedule,
                'interval': None,
                'solar': None,
                'clocked': None,
                'args': '[]',
                'kwargs': '{}',
                'enabled': True,
                'description': 'Envia lembretes uma hora antes de partidas analisadas.',
            },
        )
        self.stdout.write(self.style.SUCCESS('Agendamentos de previews e push sincronizados.'))
