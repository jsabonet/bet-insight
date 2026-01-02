#!/bin/bash
set -e

echo "Aguardando banco de dados..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "Postgres indisponível - aguardando..."
  sleep 2
done

echo "Banco de dados disponível!"

echo "Executando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Iniciando servidor..."
exec "$@"
