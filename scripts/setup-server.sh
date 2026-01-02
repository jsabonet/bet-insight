#!/bin/bash

# Script de deploy inicial para Digital Ocean Droplet
# Execute este script após clonar o repositório no servidor

set -e

echo "==================================="
echo "PlacarCerto - Deploy Inicial"
echo "==================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute como root ou com sudo"
    exit 1
fi

# Atualizar sistema
echo "1. Atualizando sistema..."
apt-get update
apt-get upgrade -y

# Instalar Docker
echo "2. Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker já instalado"
fi

# Instalar Docker Compose
echo "3. Instalando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose já instalado"
fi

# Criar usuário para a aplicação (se não existir)
echo "4. Configurando usuário da aplicação..."
if ! id "appuser" &>/dev/null; then
    useradd -m -s /bin/bash appuser
    usermod -aG docker appuser
    echo "Usuário 'appuser' criado"
else
    echo "Usuário 'appuser' já existe"
fi

# Criar diretório da aplicação
echo "5. Configurando diretórios..."
APP_DIR="/home/appuser/placarcerto"
mkdir -p $APP_DIR
chown -R appuser:appuser $APP_DIR

# Configurar firewall
echo "6. Configurando firewall..."
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw reload

# Instalar ferramentas úteis
echo "7. Instalando ferramentas auxiliares..."
apt-get install -y git curl wget nano htop

echo ""
echo "==================================="
echo "Instalação inicial concluída!"
echo "==================================="
echo ""
echo "Próximos passos:"
echo "1. Clone o repositório em $APP_DIR"
echo "2. Copie e configure os arquivos .env.production"
echo "3. Execute ./scripts/deploy.sh para iniciar a aplicação"
echo ""
echo "Para mudar para o usuário da aplicação:"
echo "  su - appuser"
echo ""
