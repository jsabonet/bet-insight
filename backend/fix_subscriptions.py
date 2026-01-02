"""
Script para criar subscription para pagamento completed sem subscription
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.subscriptions.models import Payment, Subscription
from django.utils import timezone
from datetime import timedelta

# Buscar pagamentos completed sem subscription
payments = Payment.objects.filter(status='completed', subscription=None)

print(f"📋 Encontrados {payments.count()} pagamentos completed sem subscription")

for payment in payments:
    plan_slug = (payment.metadata or {}).get('plan', 'teste')
    plan_map = {
        'monthly': 'monthly',
        'quarterly': 'quarterly',
        'yearly': 'yearly',
        'starter': 'monthly',
        'pro': 'monthly',
        'vip': 'monthly',
        'teste': 'monthly',
    }
    plan_choice = plan_map.get(plan_slug, 'monthly')
    
    # Calcular end_date
    start_date = payment.completed_at or timezone.now()
    if plan_slug == 'teste':
        end_date = start_date + timedelta(days=1)
    elif plan_choice == 'monthly':
        end_date = start_date + timedelta(days=30)
    elif plan_choice == 'quarterly':
        end_date = start_date + timedelta(days=90)
    elif plan_choice == 'yearly':
        end_date = start_date + timedelta(days=365)
    else:
        end_date = start_date + timedelta(days=30)
    
    # Criar subscription
    subscription = Subscription.objects.create(
        user=payment.user,
        plan=plan_choice,
        status='active',
        start_date=start_date,
        end_date=end_date,
        auto_renew=True,
        amount_paid=payment.amount,
    )
    
    payment.subscription = subscription
    payment.save()
    
    print(f"✅ Subscription criada para pagamento {payment.transaction_id}")
    print(f"   User: {payment.user.email}")
    print(f"   Plan: {plan_choice} ({plan_slug})")
    print(f"   Start: {start_date}")
    print(f"   End: {end_date}")

print("\n✅ Processo concluído!")
