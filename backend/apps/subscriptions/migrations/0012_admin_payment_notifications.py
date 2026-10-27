from datetime import timedelta

from django.db import migrations, models
from django.utils import timezone


def mark_existing_payment_events(apps, schema_editor):
    Payment = apps.get_model('subscriptions', 'Payment')
    now = timezone.now()
    Payment.objects.filter(status='completed').update(
        admin_sale_email_sent_at=now,
        admin_sale_push_sent_at=now,
    )
    Payment.objects.filter(
        gateway='vpay',
        status='pending',
        created_at__lte=now - timedelta(hours=1),
    ).exclude(vpay_order_id='').update(
        admin_abandoned_email_sent_at=now,
        admin_abandoned_push_sent_at=now,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0011_payment_recovery_email_sent_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='admin_sale_email_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='admin_sale_push_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='admin_abandoned_email_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='admin_abandoned_push_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(mark_existing_payment_events, migrations.RunPython.noop),
    ]
