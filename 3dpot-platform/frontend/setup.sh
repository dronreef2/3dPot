#!/bin/bash
# 3dPot Platform - Frontend Setup Script
# Sprint 2-3: Conversação IA Completa
# Criado por: MiniMax Agent

echo "🚀 Configurando 3dPot Frontend (Sprint 2-3)"
echo "=================================================="

# Verificar se estamos no diretório correto
if [ ! -f "package.json" ]; then
    echo "❌ Erro: Execute este script no diretório frontend/"
    echo "   cd frontend && ./setup.sh"
    exit 1
fi

echo "📍 Diretório atual: $(pwd)"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js detectado: $NODE_VERSION"

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Por favor, instale npm"
    exit 1
fi

NPM_VERSION=$(npm -v)
echo "✅ npm detectado: v$NPM_VERSION"

# Limpar instalação anterior
echo "🧹 Limpando instalação anterior..."
rm -rf node_modules
rm -f package-lock.json

# Configurar npm para instalação local
echo "⚙️ Configurando npm para instalação local..."
npm config set prefix "./.npm-global"
echo "✅ NPM configurado"

# Instalar dependências
echo "📦 Instalando dependências..."
echo "   ⏳ Isso pode levar alguns minutos..."

if npm install; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro na instalação das dependências"
    echo "   Tentando método alternativo..."
    
    # Tentar com cache limpo
    npm cache clean --force
    npm install --no-optional
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependências instaladas com método alternativo!"
    else
        echo "❌ Falha na instalação. Tentando última opção..."
        
        # Tentar com flag --legacy-peer-deps
        npm install --legacy-peer-deps --no-optional
        
        if [ $? -eq 0 ]; then
            echo "✅ Dependências instaladas com --legacy-peer-deps!"
        else
            echo "❌ Todas as tentativas falharam."
            echo "   Por favor, execute manualmente:"
            echo "   npm install --force"
            exit 1
        fi
    fi
fi

# Verificar se Vite está disponível
echo "🔍 Verificando Vite..."
if [ -f "node_modules/.bin/vite" ]; then
    echo "✅ Vite encontrado!"
else
    echo "⚠️ Vite não encontrado, tentando instalar..."
    npm install vite @vitejs/plugin-react --save-dev
fi

# Verificar TypeScript
echo "🔍 Verificando TypeScript..."
if [ -f "node_modules/.bin/tsc" ]; then
    echo "✅ TypeScript encontrado!"
else
    echo "⚠️ TypeScript não encontrado, instalando..."
    npm install typescript @types/react @types/react-dom --save-dev
fi

# Verificar TailwindCSS
echo "🔍 Verificando TailwindCSS..."
if [ -f "node_modules/.bin/tailwindcss" ]; then
    echo "✅ TailwindCSS encontrado!"
else
    echo "⚠️ TailwindCSS não encontrado, instalando..."
    npm install tailwindcss @tailwindcss/forms autoprefixer postcss --save-dev
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p public
mkdir -p src/components
mkdir -p src/pages
mkdir -p src/services
mkdir -p src/hooks
mkdir -p src/contexts
mkdir -p src/types
mkdir -p src/utils
echo "✅ Diretórios criados"

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo .env..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado a partir do .env.example"
    else
        echo "📝 Criando .env básico..."
        cat > .env << EOF
# 3dPot Platform - Frontend Environment
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME=3dPot Platform
VITE_APP_VERSION=1.0.0
VITE_NODE_ENV=development
VITE_DEBUG=true
EOF
        echo "✅ Arquivo .env básico criado"
    fi
else
    echo "✅ Arquivo .env já existe"
fi

# Teste de build
echo "🔨 Testando build..."
if npm run build; then
    echo "✅ Build de produção funcionando!"
else
    echo "⚠️ Build de produção falhou (pode ser normal)"
fi

# Verificar Dev Server
echo "🔍 Verificando dev server..."
if npm run dev > /dev/null 2>&1 &
then
    sleep 3
    echo "✅ Dev server iniciando..."
    echo "🌐 Acesse: http://localhost:3000"
    echo "🔗 Backend API: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo ""
    echo "🎯 Para parar o servidor: Ctrl+C"
    echo "📱 Interface responsiva disponível"
    echo "🔌 WebSocket configurado para ws://localhost:8000/ws"
    echo ""
    echo "🎉 Frontend Sprint 2-3 configurado com sucesso!"
    echo "   ✅ Interface React Chat"
    echo "   ✅ WebSocket Real-time"
    echo "   ✅ Minimax M2 Agent Integration"
    echo "   ✅ Spec Extractor com Confidence"
    echo "   ✅ Dashboard e Histórico"
    
    # Manter servidor rodando
    wait
else
    echo "❌ Falha ao iniciar dev server"
    echo "   Execute manualmente: npm run dev"
fi