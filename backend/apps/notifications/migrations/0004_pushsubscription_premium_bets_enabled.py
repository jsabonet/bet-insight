from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_pushsubscription_event_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushsubscription',
            name='premium_bets_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
