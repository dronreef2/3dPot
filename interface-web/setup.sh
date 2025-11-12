#!/bin/bash

# 3dPot Dashboard - Sprint 4 Setup Script
# Automatiza a instalação e configuração do sistema

echo "🚀 3dPot Dashboard - Sprint 4 Setup"
echo "===================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se Node.js está instalado
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js não encontrado. Instale Node.js 18+ primeiro."
        echo "Download: https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ $MAJOR_VERSION -lt 18 ]; then
        print_error "Node.js versão $NODE_VERSION encontrada. Requer versão 18+."
        exit 1
    fi
    
    print_status "Node.js $NODE_VERSION encontrado"
}

# Verificar se npm está instalado
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_error "npm não encontrado."
        exit 1
    fi
    
    NPM_VERSION=$(npm -v)
    print_status "npm $NPM_VERSION encontrado"
}

# Instalar dependências
install_dependencies() {
    print_info "Instalando dependências..."
    
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    
    if [ $? -eq 0 ]; then
        print_status "Dependências instaladas com sucesso"
    else
        print_error "Falha ao instalar dependências"
        exit 1
    fi
}

# Verificar estrutura do projeto
check_project_structure() {
    print_info "Verificando estrutura do projeto..."
    
    REQUIRED_FILES=(
        "package.json"
        "vite.config.ts"
        "tsconfig.json"
        "tailwind.config.js"
        "src/App.tsx"
        "src/main.tsx"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Arquivo obrigatório não encontrado: $file"
            exit 1
        fi
    done
    
    print_status "Estrutura do projeto verificada"
}

# Criar arquivo de ambiente
create_env_file() {
    if [ ! -f ".env" ]; then
        print_info "Criando arquivo .env..."
        cat > .env << EOL
# 3dPot Dashboard Environment Configuration
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000

# Development settings
VITE_DEV_MODE=true
VITE_MOCK_DATA=true
EOL
        print_status "Arquivo .env criado"
    else
        print_info "Arquivo .env já existe, mantendo..."
    fi
}

# Executar build de teste
test_build() {
    print_info "Executando build de teste..."
    
    npm run build
    
    if [ $? -eq 0 ]; then
        print_status "Build de teste concluído com sucesso"
        print_info "Arquivos de build disponíveis na pasta 'dist/'"
    else
        print_error "Falha no build de teste"
        exit 1
    fi
}

# Mostrar comandos de execução
show_commands() {
    echo ""
    echo "🎯 Comandos para executar o projeto:"
    echo "=================================="
    echo ""
    echo -e "${GREEN}Desenvolvimento:${NC}"
    echo "  npm run dev          - Executar frontend (porta 3000)"
    echo "  npm run server       - Executar backend (porta 5000)"
    echo "  npm run start        - Executar frontend + backend"
    echo ""
    echo -e "${GREEN}Build e Deploy:${NC}"
    echo "  npm run build        - Build para produção"
    echo "  npm run preview      - Preview da build"
    echo ""
    echo -e "${GREEN}Credenciais de Teste:${NC}"
    echo "  Admin:    admin / 123456"
    echo "  Operator: operator / 123456"
    echo "  Viewer:   viewer / 123456"
    echo ""
    echo -e "${BLUE}URLs de Acesso:${NC}"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:5000"
    echo ""
}

# Menu principal
main_menu() {
    echo ""
    echo "📋 Escolha uma opção:"
    echo "1) Instalação completa (recomendado)"
    echo "2) Apenas instalar dependências"
    echo "3) Verificar sistema apenas"
    echo "4) Sair"
    echo ""
    read -p "Digite sua escolha (1-4): " choice
    
    case $choice in
        1)
            print_info "Iniciando instalação completa..."
            check_node
            check_npm
            check_project_structure
            install_dependencies
            create_env_file
            test_build
            show_commands
            ;;
        2)
            print_info "Instalando dependências..."
            check_node
            check_npm
            install_dependencies
            show_commands
            ;;
        3)
            print_info "Verificando sistema..."
            check_node
            check_npm
            check_project_structure
            print_status "Sistema verificado com sucesso!"
            ;;
        4)
            print_info "Saindo..."
            exit 0
            ;;
        *)
            print_error "Opção inválida"
            main_menu
            ;;
    esac
}

# Verificar se estamos no diretório correto
if [ ! -f "package.json" ]; then
    print_error "Execute este script no diretório 'interface-web/'"
    print_info "Certifique-se de estar no diretório correto:"
    print_info "cd interface-web"
    exit 1
fi

# Executar menu principal
main_menu

print_status "Setup concluído com sucesso! 🎉"
print_info "Execute 'npm run dev' para iniciar o projeto"