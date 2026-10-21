#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'

RESTART_RUNNING=false
if [[ "${1:-}" == "--restart" ]]; then
    RESTART_RUNNING=true
    shift
fi
if [[ "$#" -gt 0 ]]; then
    printf 'Uso: bash scripts/update-production.sh [--restart]\n' >&2
    exit 2
fi

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

process_tree=()
collect_process_tree() {
    local parent="$1"
    local child

    while IFS= read -r child; do
        [[ -n "$child" ]] && collect_process_tree "$child"
    done < <(ps -o pid= --ppid "$parent")
    process_tree+=("$parent")
}

stop_previous_update() {
    local lock_file="$1"
    local current_pid="$2"
    local process_id
    local process_command
    local process_directory
    local found_update=false
    local lock_pids
    local acquired=false
    local attempt

    for command in fuser ps readlink; do
        command -v "$command" >/dev/null 2>&1 || fail \
            "A opção --restart requer o comando $command."
    done

    lock_pids="$(fuser -f "$lock_file" 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+$' || true)"
    while IFS= read -r process_id; do
        [[ -n "$process_id" && "$process_id" != "$current_pid" ]] || continue

        process_command="$(ps -p "$process_id" -o args= 2>/dev/null || true)"
        process_directory="$(readlink -f "/proc/$process_id/cwd" 2>/dev/null || true)"
        if [[ "$process_directory" == "$PROJECT_DIR" ]] &&
            printf '%s\n' "$process_command" |
                grep -Eq '(^|[[:space:]/])update-production\.sh([[:space:]]|$)'; then
            if [[ "$found_update" == true ]]; then
                fail "Mais de uma execução do atualizador foi encontrada; nenhum processo foi terminado."
            fi
            found_update=true
            collect_process_tree "$process_id"
        fi
    done <<< "$lock_pids"

    [[ "$found_update" == true ]] || fail \
        "O bloqueio está ocupado, mas não foi possível confirmar uma execução deste atualizador neste projeto. Nenhum processo foi terminado."

    log "A terminar a execução anterior do atualizador e os seus processos descendentes (opção --restart)..."
    for process_id in "${process_tree[@]}"; do
        kill -TERM "$process_id" 2>/dev/null || true
    done

    for ((attempt = 1; attempt <= 15; attempt++)); do
        if flock -n 9; then
            acquired=true
            break
        fi
        sleep 1
    done

    if [[ "$acquired" != true ]]; then
        log "A execução anterior não terminou com SIGTERM; a forçar o encerramento da árvore identificada."
        for process_id in "${process_tree[@]}"; do
            kill -KILL "$process_id" 2>/dev/null || true
        done
        for ((attempt = 1; attempt <= 5; attempt++)); do
            if flock -n 9; then
                acquired=true
                break
            fi
            sleep 1
        done
    fi

    [[ "$acquired" == true ]] || fail \
        "Não foi possível libertar o bloqueio após terminar a execução anterior."
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
LOCK_FILE="$BACKUP_DIR/.update-production.lock"
exec 9>>"$LOCK_FILE"
if ! flock -n 9; then
    if [[ "$RESTART_RUNNING" != true ]]; then
        fail "Já existe outra atualização em execução. Aguarde-a terminar ou use --restart para terminá-la explicitamente."
    fi
    stop_previous_update "$LOCK_FILE" "$$"
fi
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
