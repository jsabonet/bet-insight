"""
Script para tornar paysuite_reference nullable
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    print("⚙️ Tornando campo paysuite_reference nullable...")
    cursor.execute("""
        ALTER TABLE subscriptions_payment 
        ALTER COLUMN paysuite_reference DROP NOT NULL
    """)
    print("✅ Campo paysuite_reference agora é nullable!")
