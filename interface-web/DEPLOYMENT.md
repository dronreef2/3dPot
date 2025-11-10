# 3dPot - Guia de Deployment em Produção

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Instalação Automatizada](#instalação-automatizada)
4. [Instalação Manual](#instalação-manual)
5. [Configuração de Hardware](#configuração-de-hardware)
6. [Monitoramento](#monitoramento)
7. [Backup e Recuperação](#backup-e-recuperação)
8. [Manutenção](#manutenção)
9. [Troubleshooting](#troubleshooting)
10. [Segurança](#segurança)

## 🎯 Visão Geral

O sistema 3dPot é uma plataforma completa para controle e monitoramento de equipamentos de impressão 3D, incluindo:

- **Monitor de Filamento ESP32**: Controle de peso, temperatura, umidade e bateria
- **Esteira Transportadora Arduino**: Controle de velocidade, direção e posição
- **Estação QC Raspberry Pi**: Análise de qualidade com visão computacional
- **Interface Web**: Dashboard responsivo com monitoramento em tempo real
- **API REST**: Integração com sistemas externos
- **WebSocket**: Comunicação em tempo real
- **Sistema de Autenticação**: JWT com controle de acesso baseado em roles
- **Monitoramento**: Prometheus + Grafana para métricas e alertas
- **Backup Automático**: Sistema de backup com retenção configurável

## 🔧 Pré-requisitos

### Servidor de Produção
- **SO**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: Mínimo 4GB, recomendado 8GB
- **Storage**: Mínimo 50GB SSD
- **CPU**: 2+ cores
- **Rede**: IP estático, portas 80 e 443 liberadas

### Software Necessário
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git
sudo apt update
sudo apt install -y git

# Ferramentas adicionais
sudo apt install -y curl wget unzip htop iotop ncdu
```

### DNS e Domínio
- Configure o DNS A record para apontar para o IP do servidor
- Exemplo: `3dpot.com.br` → `SEU_IP_PUBLICO`
- Configure também `www.3dpot.com.br` se necessário

## 🚀 Instalação Automatizada

### 1. Clone o Repositório
```bash
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot/interface-web
```

### 2. Execute o Script de Deploy
```bash
# Tornar o script executável
chmod +x deploy.sh

# Deploy completo
./deploy.sh deploy
```

O script automatizado irá:
- ✅ Verificar pré-requisitos
- ✅ Configurar diretórios
- ✅ Criar arquivo `.env`
- ✅ Configurar SSL com Let's Encrypt
- ✅ Construir containers Docker
- ✅ Iniciar todos os serviços
- ✅ Configurar firewall
- ✅ Configurar backup automático
- ✅ Executar health check

### 3. Configurações Pós-Deploy
```bash
# Acessar o diretório do projeto
cd /opt/3dpot

# Editar configurações
nano .env

# Reiniciar após mudanças
docker-compose restart
```

## 🛠️ Instalação Manual

### 1. Preparação do Ambiente
```bash
# Criar diretórios
sudo mkdir -p /opt/3dpot
sudo chown $USER:$USER /opt/3dpot
cd /opt/3dpot

# Clonar repositório
git clone https://github.com/dronreef2/3dPot.git .
cd interface-web
```

### 2. Configurar Variáveis de Ambiente
```bash
# Copiar template
cp .env.example .env

# Editar configurações
nano .env
```

### 3. Construir e Iniciar Serviços
```bash
# Construir imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps
```

### 4. Configurar SSL
```bash
# Parar Nginx
docker-compose stop nginx

# Instalar Certbot
sudo apt install -y certbot

# Obter certificado
sudo certbot certonly --standalone -d 3dpot.com.br -d www.3dpot.com.br --email admin@3dpot.com.br --agree-tos --no-eff-email

# Copiar certificados
sudo cp /etc/letsencrypt/live/3dpot.com.br/fullchain.pem nginx/ssl/3dpot.crt
sudo cp /etc/letsencrypt/live/3dpot.com.br/privkey.pem nginx/ssl/3dpot.key
sudo chown $USER:$USER nginx/ssl/*

# Reiniciar Nginx
docker-compose up -d nginx
```

### 5. Configurar Firewall
```bash
# Instalar UFW
sudo apt install -y ufw

# Configurar regras
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Configurar rate limiting (opcional)
sudo ufw limit ssh
```

## 🔌 Configuração de Hardware

### ESP32 - Monitor de Filamento
```bash
# Conectar via MQTT
# Configurar WiFi no código
# Tópicos MQTT:
# - 3dpot/esp32/weight
# - 3dpot/esp32/temperature
# - 3dpot/esp32/humidity
# - 3dpot/esp32/battery
```

### Arduino - Esteira Transportadora
```bash
# Conectar via USB
# Porta serial: /dev/ttyACM0
# Comandos disponíveis:
# - START, STOP, SPEED:value, DIRECTION:forward/backward
# - GET_STATUS, GET_POSITION, TARE
```

### Raspberry Pi - Estação QC
```bash
# API REST: http://raspberry-pi:5000
# Endpoints:
# - GET /api/quality/status
# - POST /api/quality/inspect
# - GET /api/quality/history
```

## 📊 Monitoramento

### Acesso aos Painéis
- **Grafana**: http://SEU_IP:3001
  - Usuário: `admin`
  - Senha: `admin123` (alterar no primeiro login)
- **Prometheus**: http://SEU_IP:9090
- **Node-RED**: http://SEU_IP:1880

### Métricas Disponíveis
- Status dos dispositivos
- Uso de CPU e memória
- Latência da API
- Taxa de erros
- Uso de banco de dados
- Alertas de hardware

### Configurar Alertas
1. Acesse Grafana em http://SEU_IP:3001
2. Vá em Alerting → Contact points
3. Configure email ou Slack
4. Importe dashboards em `monitoring/grafana/dashboards/`

## 💾 Backup e Recuperação

### Backup Automático
```bash
# Verificar status do backup
docker logs 3dpot-backup

# Backup manual
docker exec 3dpot-backup /backup.sh

# Listar backups
ls /opt/3dpot-backups/
```

### Restaurar Backup
```bash
# Parar serviços
docker-compose down

# Extrair backup
tar -xzf /opt/3dpot-backups/3dpot-backup-YYYYMMDD-HHMMSS.tar.gz -C /opt/3dpot

# Iniciar serviços
docker-compose up -d
```

### Configurar Backups Remotos (AWS S3)
```bash
# Instalar AWS CLI
sudo apt install awscli

# Configurar credenciais
aws configure

# Modificar script de backup para upload S3
nano scripts/backup.sh
# Adicionar: aws s3 cp $BACKUP_FILE s3://seu-bucket/3dpot/
```

## 🔧 Manutenção

### Comandos Úteis
```bash
# Status geral
./deploy.sh status

# Reiniciar todos os serviços
./deploy.sh restart

# Ver logs
./deploy.sh logs backend
./deploy.sh logs frontend
./deploy.sh logs nginx

# Atualizar aplicação
./deploy.sh update

# Parar serviços
./deploy.sh stop

# Limpar recursos
docker system prune -a
```

### Limpeza de Logs
```bash
# Rotação manual
sudo logrotate /etc/logrotate.d/3dpot

# Limpar logs Docker
docker system prune --volumes
```

### Atualizações
```bash
# Atualizar código
cd /opt/3dpot
git pull origin main

# Rebuild e restart
docker-compose build --no-cache
docker-compose up -d

# Rollback se necessário
./deploy.sh rollback /opt/3dpot-backups/backup-YYYYMMDD-HHMMSS.tar.gz
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Backend não inicia
```bash
# Verificar logs
docker logs 3dpot-backend

# Verificar arquivo .env
cat /opt/3dpot/.env

# Verificar permissões
sudo chown -R 1001:1001 /opt/3dpot/
```

#### 2. SSL não funciona
```bash
# Verificar certificados
ls -la /opt/3dpot/nginx/ssl/

# Verificar configuração Nginx
docker exec 3dpot-nginx nginx -t

# Renovar certificado
sudo certbot renew
```

#### 3. Hardware não conecta
```bash
# Verificar dispositivos USB
lsusb
dmesg | grep tty

# Verificar permissões serial
sudo usermod -a -G dialout $USER

# Verificar configuração
docker exec 3dpot-backend curl -f http://localhost:3000/api/health
```

#### 4. Performance baixa
```bash
# Verificar recursos
htop
docker stats

# Otimizar containers
docker-compose down
# Editar docker-compose.yml para aumentar recursos
docker-compose up -d
```

### Logs de Debug
```bash
# Logs de todos os serviços
docker-compose logs --tail=100

# Logs específicos
docker logs -f 3dpot-backend
docker logs -f 3dpot-nginx
docker logs -f 3dpot-mqtt

# Verificar conectividade
curl -v http://localhost/api/health
```

## 🔒 Segurança

### Configurações de Segurança Implementadas
- ✅ SSL/TLS obrigatório com Let's Encrypt
- ✅ Headers de segurança (HSTS, CSP, X-Frame-Options)
- ✅ Rate limiting na API
- ✅ Autenticação JWT com expiração
- ✅ Senhas hasheadas com bcrypt
- ✅ Firewall configurado (UFW)
- ✅ Contêineres rodando como usuários não-root
- ✅ Logs de auditoria
- ✅ Backup criptografado
- ✅ Variáveis de ambiente seguras

### Verificações de Segurança
```bash
# Testar SSL
curl -I https://3dpot.com.br

# Verificar headers
curl -I http://localhost/ | grep -E "(X-|Strict)"

# Verificar portas abertas
sudo netstat -tlnp

# Verificar usuários
who
last
```

### Hardening Adicional
```bash
# Desabilitar root SSH
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Configurar fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 📱 URLs de Acesso

Após o deploy bem-sucedido, acesso:

- **Frontend**: https://3dpot.com.br
- **API**: https://3dpot.com.br/api
- **WebSocket**: wss://3dpot.com.br/socket.io/
- **Grafana**: http://SEU_IP:3001
- **Prometheus**: http://SEU_IP:9090
- **Node-RED**: http://SEU_IP:1880

## 🆘 Suporte

Para suporte e documentação adicional:
- **GitHub**: https://github.com/dronreef2/3dPot
- **Issues**: https://github.com/dronreef2/3dPot/issues
- **Wiki**: https://github.com/dronreef2/3dPot/wiki

## 📄 Changelog

### v1.0.0 - Deploy Production Ready
- ✅ Sistema completo de deployment
- ✅ Docker multi-stage otimizado
- ✅ SSL automático com Let's Encrypt
- ✅ Monitoramento completo (Prometheus + Grafana)
- ✅ Backup automático configurado
- ✅ Segurança implementada
- ✅ Documentação completa
- ✅ Scripts de automação

---

**Última atualização**: 2025-11-10
**Autor**: MiniMax Agent
**Versão**: 1.0.0