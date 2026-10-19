"""Valor da aposta do snapshot passa a ser em MT (1:1), não em unidades."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0008_normalize_social_proof_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialproofticket',
            name='stake_units',
            field=models.FloatField(
                default=10.0,
                help_text='Valor em meticais aplicado directamente no bilhete (1:1).',
                verbose_name='Valor da Aposta (MT)',
            ),
        ),
    ]
