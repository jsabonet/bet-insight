#!/bin/bash

# Cria/ativa swap em servidores com pouca RAM (droplets de 512 MB - 1 GB).
# Sem swap, o build Docker (npm run build / apt-get / pip) e morto pelo
# OOM killer e o deploy parece "travado" por varios minutos.
#
# Uso (como root): ./scripts/setup-swap.sh [tamanho_em_MB]
# Ex.: ./scripts/setup-swap.sh 2048

set -e

SWAP_FILE="/swapfile"
SWAP_SIZE_MB="${1:-2048}"

if [ "$(id -u)" -ne 0 ]; then
    echo "Erro: execute como root (sudo ./scripts/setup-swap.sh)"
    exit 1
fi

if [ "$(swapon --show --noheadings | wc -l)" -gt 0 ]; then
    echo "Swap ja ativo:"
    swapon --show
    exit 0
fi

if [ -f "$SWAP_FILE" ]; then
    echo "Reutilizando $SWAP_FILE existente..."
else
    # fallocate nao funciona em alguns filesystems (ex.: ZFS/overlay);
    # nesse caso usamos dd.
    echo "Criando ${SWAP_SIZE_MB} MB em $SWAP_FILE..."
    if ! fallocate -l "${SWAP_SIZE_MB}M" "$SWAP_FILE" 2>/dev/null; then
        dd if=/dev/zero of="$SWAP_FILE" bs=1M count="$SWAP_SIZE_MB" status=progress
    fi
    chmod 600 "$SWAP_FILE"
    mkswap "$SWAP_FILE"
fi

swapon "$SWAP_FILE"

# Persistir no fstab (apenas uma vez)
if ! grep -q "^$SWAP_FILE" /etc/fstab; then
    echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
fi

# swappiness baixo: preferir RAM, usar swap so quando necessario
if [ -f /etc/sysctl.conf ] && ! grep -q '^vm.swappiness' /etc/sysctl.conf; then
    echo "vm.swappiness=10" >> /etc/sysctl.conf
fi
sysctl -w vm.swappiness=10 >/dev/null

echo ""
echo "Swap ativo:"
swapon --show
free -h
