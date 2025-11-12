#!/bin/bash
# 3dPot Backend - Script de Inicialização Rápida

echo "🚀 3dPot Backend - Inicialização Rápida"
echo "========================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale pip"
    exit 1
fi

# Instalar dependências se não existirem
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Configurar .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️ Configurando variáveis de ambiente..."
    cp .env.example .env
    echo "ℹ️  Arquivo .env criado. Configure conforme necessário."
fi

# Inicializar banco de dados
echo "🗄️ Inicializando banco de dados..."
python3 init_backend.py

# Iniciar servidor FastAPI
echo "🌐 Iniciando servidor FastAPI..."
echo "📖 Documentação: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Para parar o servidor, pressione Ctrl+C"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
