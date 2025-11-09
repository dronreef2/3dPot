#!/bin/bash

# Setup Automatizado do 3D Pot
# Autor: MiniMax Agent
# Data: 2025-11-10

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar com cor
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}"
}

# Verificar se está executando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script não deve ser executado como root"
        print_status "Execute: ./setup-3dpot.sh"
        exit 1
    fi
}

# Verificar se é Ubuntu/Debian
check_distro() {
    if ! command -v apt &> /dev/null; then
        print_error "Este script é compatível apenas com Ubuntu/Debian"
        exit 1
    fi
}

# Atualizar sistema
update_system() {
    print_header "Atualizando Sistema"
    print_status "Atualizando lista de pacotes..."
    sudo apt update
    print_status "Instalando atualizações..."
    sudo apt upgrade -y
}

# Instalar ferramentas básicas
install_basic_tools() {
    print_header "Instalando Ferramentas Básicas"
    
    local tools=("curl" "wget" "git" "vim" "htop" "unzip" "python3" "python3-pip" "python3-venv" "nodejs" "npm")
    
    for tool in "${tools[@]}"; do
        print_status "Instalando $tool..."
        sudo apt install -y "$tool"
    done
    
    # Verificar versões
    print_status "Versões instaladas:"
    echo "Git: $(git --version)"
    echo "Python3: $(python3 --version)"
    echo "NodeJS: $(node --version)"
    echo "NPM: $(npm --version)"
}

# Instalar ferramentas de desenvolvimento
install_dev_tools() {
    print_header "Instalando Ferramentas de Desenvolvimento"
    
    # VSCode
    print_status "Instalando Visual Studio Code..."
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
    sudo apt update
    sudo apt install -y code
    
    # Arduino IDE
    print_status "Instalando Arduino IDE..."
    sudo apt install -y arduino
    
    # PlatformIO via pip
    print_status "Instalando PlatformIO..."
    pip3 install platformio
}

# Instalar ferramentas 3D
install_3d_tools() {
    print_header "Instalando Ferramentas 3D"
    
    # FreeCAD
    print_status "Instalando FreeCAD..."
    sudo apt install -y freecad
    
    # OpenSCAD
    print_status "Instalando OpenSCAD..."
    sudo apt install -y openscad
    
    # Cura (via AppImage)
    print_status "Baixando Ultimaker Cura..."
    if [ ! -f "Ultimaker-Cura-5.9.0-linux-modern.AppImage" ]; then
        wget https://github.com/Ultimaker/Cura/releases/download/5.9.0/Ultimaker-Cura-5.9.0-linux-modern.AppImage
        chmod +x Ultimaker-Cura-5.9.0-linux-modern.AppImage
        sudo mv Ultimaker-Cura-5.9.0-linux-modern.AppImage /opt/
        sudo ln -sf /opt/Ultimaker-Cura-5.9.0-linux-modern.AppImage /usr/local/bin/cura
    fi
    
    # PrusaSlicer
    print_status "Baixando PrusaSlicer..."
    if [ ! -d "PrusaSlicer-2.8.1" ]; then
        wget https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.8.1/PrusaSlicer-2.8.1+linux-x64-202407261536.tar.gz
        tar -xzf PrusaSlicer-*.tar.gz
        sudo mv PrusaSlicer-2.8.1+linux-x64-202407261536 /opt/prusaslicer
        sudo ln -sf /opt/prusaslicer/bin/prusaslicer /usr/local/bin/prusaslicer
    fi
}

# Instalar IoT tools
install_iot_tools() {
    print_header "Instalando Ferramentas IoT"
    
    # Mosquitto MQTT
    print_status "Instalando Mosquitto MQTT Broker..."
    sudo apt install -y mosquitto mosquitto-clients
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    
    # Node-RED
    print_status "Instalando Node-RED..."
    sudo npm install -g node-red
    sudo systemctl enable nodered
    
    # Python IoT packages
    print_status "Instalando packages Python para IoT..."
    pip3 install --user paho-mqtt requests flask numpy opencv-python
    
    # Adicionar packages para Raspberry Pi (se aplicável)
    if grep -q "Raspberry" /proc/device-tree/model 2>/dev/null; then
        print_status "Detectado Raspberry Pi - instalando packages específicos..."
        pip3 install --user RPi.GPIO picamera2 gpiozero
    fi
}

# Configurar workspace
setup_workspace() {
    print_header "Configurando Workspace"
    
    # Criar estrutura de diretórios
    local workspace_dir="$HOME/3dpot-workspace"
    mkdir -p "$workspace_dir"
    
    # Criar diretórios para cada projeto
    mkdir -p "$workspace_dir"/{esp32,arduino,raspberry-pi,models-3d,scripts,docs}
    
    # Criar script de desenvolvimento
    cat > "$workspace_dir/dev-setup.sh" << 'EOF'
#!/bin/bash
# Script de desenvolvimento 3D Pot

echo "Iniciando ambiente de desenvolvimento 3D Pot..."

# Iniciar Mosquitto se não estiver rodando
if ! pgrep -x "mosquitto" > /dev/null; then
    echo "Iniciando Mosquitto..."
    mosquitto -d
fi

# Iniciar Node-RED se não estiver rodando
if ! pgrep -x "node-red" > /dev/null; then
    echo "Iniciando Node-RED..."
    nohup node-red > ~/.node-red.log 2>&1 &
fi

echo "Ambiente configurado!"
echo "- Mosquitto: $(pgrep -x 'mosquitto' > /dev/null && echo '✓' || echo '✗')"
echo "- Node-RED: $(pgrep -x 'node-red' > /dev/null && echo '✓' || echo '✗')"
echo ""
echo "Acesse:"
echo "- Node-RED: http://localhost:1880"
echo "- Mosquitto: localhost:1883"
EOF
    
    chmod +x "$workspace_dir/dev-setup.sh"
    
    # Criar .gitignore
    cat > "$workspace_dir/.gitignore" << 'EOF'
# 3D Pot - GitIgnore

# Compiled source
*.o
*.so
*.exe
*.dll
*.pyc
*.pyo

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 3D Models
*.stl
*.gcode
*.3mf

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
.DS_Store

# Arduino
*.tmp
*.bak

# Node modules
node_modules/
npm-debug.log*

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF
    
    print_status "Workspace configurado em: $workspace_dir"
}

# Verificar instalação
verify_installation() {
    print_header "Verificando Instalação"
    
    local tools=("git" "python3" "npm" "node" "arduino" "freecad" "openscad" "mosquitto")
    local failed=()
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_status "✓ $tool instalado"
        else
            print_error "✗ $tool não encontrado"
            failed+=("$tool")
        fi
    done
    
    # Verificar serviços
    if systemctl is-active --quiet mosquitto; then
        print_status "✓ Mosquitto rodando"
    else
        print_error "✗ Mosquitto não está rodando"
    fi
    
    if [ ${#failed[@]} -eq 0 ]; then
        print_status "Instalação concluída com sucesso!"
    else
        print_warning "Alguns tools falharam: ${failed[*]}"
    fi
}

# Exibir informações finais
show_final_info() {
    print_header "Instalação Concluída"
    
    echo -e "${GREEN}🎉 3D Pot setup concluído com sucesso!${NC}"
    echo ""
    echo "Ferramentas instaladas:"
    echo "- Git: $(git --version)"
    echo "- Python3: $(python3 --version)"
    echo "- Node.js: $(node --version)"
    echo "- Arduino IDE: Disponível em Applications"
    echo "- FreeCAD: Disponível em Applications"
    echo "- OpenSCAD: Disponível em Applications"
    echo "- VSCode: code (terminal) ou Applications"
    echo ""
    echo "Para começar:"
    echo "1. Execute: source $HOME/3dpot-workspace/dev-setup.sh"
    echo "2. Acesse Node-RED: http://localhost:1880"
    echo "3. Teste MQTT: mosquitto_pub -h localhost -t 'test' -m 'Hello 3D Pot'"
    echo ""
    echo "Documentação completa em: $HOME/3dpot-workspace/docs/"
}

# Função principal
main() {
    print_header "3D Pot - Setup Automatizado"
    echo "Este script irá instalar todas as ferramentas necessárias para os projetos 3D Pot"
    echo ""
    
    read -p "Deseja continuar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelado pelo usuário"
        exit 0
    fi
    
    # Verificações
    check_root
    check_distro
    
    # Instalação
    update_system
    install_basic_tools
    install_dev_tools
    install_3d_tools
    install_iot_tools
    setup_workspace
    verify_installation
    show_final_info
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
