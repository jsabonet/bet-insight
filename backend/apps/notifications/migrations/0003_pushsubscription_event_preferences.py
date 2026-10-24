from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_remove_pushsubscription_unique_user_push_endpoint_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushsubscription',
            name='match_events_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='pushsubscription',
            name='affiliate_notifications_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
