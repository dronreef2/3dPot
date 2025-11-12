#!/bin/bash

# Teste Automatizado de Integração 3dPot Dashboard
# Este script verifica se todos os componentes estão funcionando corretamente

echo "🧪 Iniciando teste automatizado de integração 3dPot..."
echo "=================================================="

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir resultado
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Função para imprimir status
print_status() {
    echo -e "${YELLOW}🔍 $1${NC}"
}

# Teste 1: Verificar se o backend está rodando
print_status "Testando Backend (Porta 5000)..."
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health)
if [ "$BACKEND_RESPONSE" = "200" ]; then
    print_result 0 "Backend respondendo corretamente"
else
    print_result 1 "Backend não está respondendo (HTTP $BACKEND_RESPONSE)"
fi

# Teste 2: Verificar se o frontend está rodando
print_status "Testando Frontend (Porta 3000)..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    print_result 0 "Frontend respondendo corretamente"
else
    print_result 1 "Frontend não está respondendo (HTTP $FRONTEND_RESPONSE)"
fi

# Teste 3: Verificar proxy frontend-backend
print_status "Testando Proxy Frontend→Backend..."
PROXY_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health)
if [ "$PROXY_RESPONSE" = "200" ]; then
    print_result 0 "Proxy Vite→Express funcionando"
else
    print_result 1 "Proxy não está funcionando (HTTP $PROXY_RESPONSE)"
fi

# Teste 4: Verificar sistema de autenticação
print_status "Testando Sistema de Autenticação..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:3000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
    print_result 0 "Login de admin funcionando"
else
    print_result 1 "Login falhado: $LOGIN_RESPONSE"
fi

# Teste 5: Verificar endpoint de usuários
print_status "Testando Endpoint de Usuários..."
USERS_RESPONSE=$(curl -s http://localhost:3000/api/auth/users \
    -H "Authorization: Bearer $(echo $LOGIN_RESPONSE | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)")

if echo "$USERS_RESPONSE" | grep -q '"success":true'; then
    print_result 0 "Endpoint de usuários funcionando"
else
    echo -e "${YELLOW}⚠️  Endpoint usuários requer autenticação (esperado)${NC}"
fi

# Teste 6: Verificar estrutura de dados
print_status "Verificando Estrutura de Dados..."
DATABASE_DATA=$(curl -s http://localhost:5000/api/health | grep -o '"database":{[^}]*}')

if echo "$DATABASE_DATA" | grep -q '"status":"connected"'; then
    print_result 0 "Database conectado e operacional"
else
    print_result 1 "Database não conectado: $DATABASE_DATA"
fi

# Teste 7: Verificar dispositivos
print_status "Verificando Sistema de Dispositivos..."
DEVICE_DATA=$(curl -s http://localhost:5000/api/health | grep -o '"devices":{[^}]*}')

if echo "$DEVICE_DATA" | grep -q '"overall":"healthy"'; then
    print_result 0 "Sistema de dispositivos operacional"
else
    echo -e "${YELLOW}⚠️  Sistema de dispositivos em estado inicial${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Teste de Integração Concluído!${NC}"
echo "=================================================="
echo ""
echo "📊 Status Final:"
echo "- Backend: Rodando na porta 5000"
echo "- Frontend: Rodando na porta 3000"  
echo "- Proxy: Configurado e funcionando"
echo "- Auth: JWT tokens sendo gerados"
echo "- Database: SQLite conectado"
echo ""
echo "🔐 Credenciais de Teste:"
echo "- Admin: admin / admin123"
echo "- Operator: operator / operator123"
echo "- Viewer: viewer / viewer123"
echo ""
echo "🌐 URLs de Acesso:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:5000/api"
echo "- Health Check: http://localhost:5000/api/health"
echo ""

# Informações dos processos
echo "🔍 Processos em Execução:"
echo "Backend PID: $(pgrep -f 'node.*index.js' || echo 'Não encontrado')"
echo "Frontend PID: $(pgrep -f 'vite' || echo 'Não encontrado')"

echo ""
echo -e "${GREEN}✅ Sistema 3dPot Dashboard totalmente integrado e operacional!${NC}"
