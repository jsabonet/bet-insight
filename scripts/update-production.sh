#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_FILE="$BACKUP_DIR/postgres-$TIMESTAMP-$$.dump"
BACKUP_TEMP=""

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

fail() {
    log "ERRO: $*"
    exit 1
}

cleanup() {
    if [[ -n "$BACKUP_TEMP" ]]; then
        rm -f -- "$BACKUP_TEMP"
    fi
}

for command in git docker curl flock; do
    command -v "$command" >/dev/null 2>&1 || fail "Comando obrigatório não encontrado: $command"
done

docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 não está disponível."

[[ -f backend/.env.production ]] || fail \
    "backend/.env.production não encontrado. Configure o ambiente de produção antes de atualizar."
[[ -f .env ]] || fail \
    ".env da raiz não encontrado. Execute o deploy inicial antes deste atualizador."
[[ -x scripts/deploy.sh ]] || fail \
    "scripts/deploy.sh não existe ou não tem permissão de execução."
[[ "$(git branch --show-current)" == "main" ]] || fail \
    "O atualizador deve ser executado na branch main."
[[ -z "$(git status --porcelain)" ]] || fail \
    "Há alterações locais no repositório. Guarde-as ou descarte-as antes de atualizar."

mkdir -p -- "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
exec 9>"$BACKUP_DIR/.update-production.lock"
flock -n 9 || fail "Já existe outra atualização em execução."
trap cleanup EXIT

log "Validando configuração Docker Compose..."
docker compose config --quiet

log "Verificando serviços existentes..."
DB_CONTAINER="$(docker compose ps --quiet db)"
if [[ -z "$DB_CONTAINER" ]]; then
    fail "O serviço db não está criado. Use scripts/deploy.sh para o primeiro deploy."
fi

log "Verificando acesso à base de dados..."
docker compose exec -T db pg_isready >/dev/null ||
    fail "A base de dados não está disponível; nenhuma atualização foi iniciada."

log "Criando backup PostgreSQL antes de atualizar código ou esquema..."
BACKUP_TEMP="$BACKUP_FILE.partial"
if ! docker compose exec -T db sh -c \
    'pg_dump --format=custom --no-owner --no-acl --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' \
    > "$BACKUP_TEMP"; then
    fail "O backup falhou. O deploy foi interrompido."
fi
[[ -s "$BACKUP_TEMP" ]] || fail "O backup ficou vazio. O deploy foi interrompido."
chmod 600 "$BACKUP_TEMP"
mv -- "$BACKUP_TEMP" "$BACKUP_FILE"
log "Backup criado: $BACKUP_FILE"

log "Executando deploy: fast-forward do Git, build, atualização dos serviços, migrações e arquivos estáticos..."
if ! "$PROJECT_DIR/scripts/deploy.sh"; then
    fail "O deploy falhou. O backup anterior à atualização foi preservado em $BACKUP_FILE."
fi

log "Validando aplicação e migrações..."
healthy=false
for ((attempt = 1; attempt <= 30; attempt++)); do
    if curl --fail --silent --show-error --max-time 5 \
        http://127.0.0.1/health >/dev/null 2>&1; then
        healthy=true
        break
    fi
    sleep 2
done
[[ "$healthy" == true ]] || fail \
    "O endpoint local /health não ficou disponível. Consulte docker compose logs."

docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py migrate --check
docker compose ps

log "Atualização concluída. Backup preservado em: $BACKUP_FILE"
