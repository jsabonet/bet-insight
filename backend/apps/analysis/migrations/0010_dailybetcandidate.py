from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0009_social_proof_stake_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyBetCandidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('fixture_id', models.PositiveBigIntegerField()),
                ('league_id', models.PositiveIntegerField(blank=True, null=True)),
                ('league_name', models.CharField(blank=True, max_length=120)),
                ('match_name', models.CharField(blank=True, max_length=240)),
                ('market', models.CharField(max_length=80)),
                ('pick', models.CharField(blank=True, max_length=160)),
                ('probability', models.FloatField()),
                ('probability_bucket', models.CharField(db_index=True, max_length=16)),
                ('odd', models.FloatField(blank=True, null=True)),
                ('ev_pct', models.FloatField(blank=True, null=True)),
                ('ranking_score', models.FloatField(blank=True, null=True)),
                ('data_quality_score', models.FloatField(blank=True, null=True)),
                ('data_completeness_pct', models.FloatField(blank=True, null=True)),
                ('selection_eligible', models.BooleanField(db_index=True, default=False)),
                ('exclusion_reason', models.CharField(blank=True, max_length=240)),
                ('outcome', models.CharField(choices=[('pending', 'Pending'), ('won', 'Won'), ('lost', 'Lost'), ('cancelled', 'Cancelled'), ('unsupported', 'Unsupported')], db_index=True, default='pending', max_length=16)),
                ('actual_result', models.CharField(blank=True, max_length=32)),
                ('home_score', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('away_score', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('model_version', models.CharField(default='dailybet-shadow-v1', max_length=32)),
                ('source_snapshot', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('settled_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'DailyBet Shadow Prediction',
                'verbose_name_plural': 'DailyBet Shadow Predictions',
                'ordering': ['-date', '-created_at'],
                'indexes': [
                    models.Index(fields=['market', 'probability_bucket', 'outcome'], name='analysis_db_market_7bf1da_idx'),
                    models.Index(fields=['league_id', 'market', 'outcome'], name='analysis_db_league__dc3f6b_idx'),
                    models.Index(fields=['date', 'selection_eligible'], name='analysis_db_date_b08f9a_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('date', 'fixture_id', 'market'), name='unique_dailybet_shadow_fixture_market'),
                ],
            },
        ),
    ]
