# Generated manually on 2026-01-01
from django.db import migrations


def migrate_old_plan_slugs(apps, schema_editor):
    """
    Migra slugs antigos para novos:
    - monthly → pro
    - quarterly → vip
    - yearly → vip (convertido para VIP trimestral com valor proporcional)
    """
    Subscription = apps.get_model('subscriptions', 'Subscription')
    
    # Mapear planos antigos para novos
    plan_mapping = {
        'monthly': 'pro',
        'quarterly': 'vip',
        'yearly': 'vip',  # Usuários anuais viram VIP
    }
    
    for old_slug, new_slug in plan_mapping.items():
        Subscription.objects.filter(plan=old_slug).update(
            plan=new_slug,
            plan_slug=new_slug
        )
    
    print(f"✅ Migrados planos antigos para novos slugs")


def reverse_migration(apps, schema_editor):
    """Reverter migração (não recomendado)"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0004_update_plan_slugs"),
    ]

    operations = [
        migrations.RunPython(migrate_old_plan_slugs, reverse_migration),
    ]
