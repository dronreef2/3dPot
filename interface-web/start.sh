#!/bin/bash

# 3dPot Dashboard - Quick Start Script
# Execução rápida do projeto

echo "🚀 3dPot Dashboard - Sprint 4 Quick Start"
echo "========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "package.json" ]; then
    echo "❌ Execute este script no diretório 'interface-web/'"
    exit 1
fi

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Falha na instalação das dependências"
        exit 1
    fi
    echo "✅ Dependências instaladas"
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️  Criando arquivo de configuração..."
    cat > .env << EOL
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
VITE_DEV_MODE=true
VITE_MOCK_DATA=true
EOL
    echo "✅ Arquivo .env criado"
fi

echo ""
echo "🎯 Iniciando 3dPot Dashboard..."
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "👤 Credenciais de login:"
echo "   Admin:    admin / 123456"
echo "   Operator: operator / 123456"
echo "   Viewer:   viewer / 123456"
echo ""
echo "📋 Funcionalidades disponíveis:"
echo "   ✅ Dashboard IoT em tempo real"
echo "   ✅ Gerenciamento de projetos 3D"
echo "   ✅ Visualizador 3D interativo"
echo "   ✅ Gráficos Chart.js"
echo "   ✅ Sistema de autenticação"
echo "   ✅ Design responsivo"
echo ""
echo "🚀 Iniciando servidor de desenvolvimento..."
echo ""

# Executar em modo desenvolvimento
npm run dev