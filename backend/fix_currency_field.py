"""
Script para adicionar valor padrão ao campo currency
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Verificar se o campo currency existe e tem constraint NOT NULL
    cursor.execute("""
        SELECT column_name, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'subscriptions_payment' AND column_name = 'currency'
    """)
    result = cursor.fetchone()
    
    if result:
        print(f"✅ Campo currency existe: nullable={result[1]}, default={result[2]}")
        
        # Se é NOT NULL sem default, adicionar default
        if result[1] == 'NO' and not result[2]:
            print("⚙️ Adicionando valor padrão 'MZN' ao campo currency...")
            cursor.execute("""
                ALTER TABLE subscriptions_payment 
                ALTER COLUMN currency SET DEFAULT 'MZN'
            """)
            print("✅ Default adicionado!")
            
            # Atualizar registros NULL existentes
            print("⚙️ Atualizando registros NULL existentes...")
            cursor.execute("""
                UPDATE subscriptions_payment 
                SET currency = 'MZN' 
                WHERE currency IS NULL
            """)
            affected = cursor.rowcount
            print(f"✅ {affected} registros atualizados!")
        else:
            print("✅ Campo já está configurado corretamente!")
    else:
        print("❌ Campo currency não existe na tabela!")
