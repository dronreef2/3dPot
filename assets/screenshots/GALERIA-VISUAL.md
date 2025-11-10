# 🎨 Galeria Visual - Projetos 3dPot

Esta galeria contém diagramas técnicos, mockups de interface e visualizações dos projetos hardware do 3dPot.

## 📁 Estrutura da Galeria

```
assets/screenshots/
├── GALERIA-VISUAL.md           # Este arquivo - índice da galeria
├── PROJETOS-DESCRICOES.md      # Descrições detalhadas para criação
├── arquitetura-esp32-monitor.png      # Diagrama arquitetura ESP32
├── arquitetura-arduino-esteira.png    # Diagrama arquitetura Arduino
├── arquitetura-raspberry-qc.png       # Diagrama arquitetura Raspberry Pi
├── fluxo-ecosistema-3dpot.png         # Fluxo integração projetos
├── interface-esp32-web.png            # Mockup interface web ESP32
├── interface-qc-dashboard.png         # Mockup dashboard estação QC
├── modelos-3d-especificacoes.png      # Especificações técnicas modelos 3D
├── esquematico-esp32-monitor.png      # Esquemático conexões ESP32
├── esquematico-arduino-esteira.png    # Esquemático conexões Arduino
├── esquematico-raspberry-qc.png       # Esquemático conexões Raspberry Pi
├── diagrama-sistema-integrado.png     # Diagrama integração global
└── GUIA-CONEXOES.md                   # Guia técnico de montagem
```

## 🖼️ Galeria de Imagens

### 1. 🏗️ Arquitetura dos Sistemas

#### **Monitor de Filamento ESP32**
![Arquitetura ESP32](arquitetura-esp32-monitor.png)
- **Descrição**: Diagrama completo da arquitetura do monitor de filamento
- **Componentes**: ESP32, HX711, interface web, MQTT, Home Assistant
- **Funcionalidades**: Monitoramento peso, alertas, web dashboard
- **Formato**: 1400x900px PNG

#### **Esteira Transportadora Arduino**
![Arquitetura Arduino](arquitetura-arduino-esteira.png)
- **Descrição**: Arquitetura completa da esteira transportadora
- **Componentes**: Arduino, motores, sensores IR, controles
- **Funcionalidades**: Controle velocidade, detecção objetos, interface
- **Formato**: 1400x1000px PNG

#### **Estação QC Raspberry Pi**
![Arquitetura QC](arquitetura-raspberry-qc.png)
- **Descrição**: Sistema de controle de qualidade com visão computacional
- **Componentes**: Raspberry Pi, câmera, OpenCV, dashboard web
- **Funcionalidades**: Análise automática, múltiplos ângulos, relatórios
- **Formato**: 1400x1100px PNG

### 2. 🔄 Fluxo de Integração

#### **Ecossistema 3dPot**
![Fluxo Ecossistema](fluxo-ecosistema-3dpot.png)
- **Descrição**: Como os três projetos se integram em um ecossistema
- **Integração**: Monitor → Esteira → QC → Produção
- **Benefícios**: Automação completa, controle qualidade, otimização
- **Formato**: 1600x800px PNG

### 3. 🖥️ Interfaces Web

#### **Interface Monitor ESP32**
![Interface Web ESP32](interface-esp32-web.png)
- **Descrição**: Mockup da interface web do monitor de filamento
- **Recursos**: Peso atual, porcentagem, gráfico histórico, alertas
- **Design**: Responsivo, cores intuitivas, controles acessíveis
- **Formato**: 1200x900px PNG

#### **Dashboard Estação QC**
![Dashboard QC](interface-qc-dashboard.png)
- **Descrição**: Interface web da estação de controle de qualidade
- **Recursos**: Status aprovação, galeria fotos, análise detalhada
- **Design**: Profissional, dados organizados, ações claras
- **Formato**: 1200x1000px PNG

### 4. 🎯 Modelos 3D Técnicos

#### **Especificações dos Modelos 3D**
![Modelos 3D](modelos-3d-especificacoes.png)
- **Descrição**: Especificações técnicas dos modelos OpenSCAD
- **Modelos**: Suporte ESP32, rolo esteira, case Raspberry Pi
- **Parâmetros**: Dimensões, tolerâncias, materiais, configurações
- **Formato**: 1400x800px PNG

### 5. 🔌 Esquemáticos Técnicos

#### **Esquemático Monitor ESP32**
![Esquemático ESP32](esquematico-esp32-monitor.png)
- **Descrição**: Diagrama detalhado de conexões do monitor de filamento
- **Componentes**: ESP32, HX711, células de carga, LED status
- **Conexões**: GPIO mapping, power distribution, sensor integration
- **Formato**: 1600x1000px PNG

#### **Esquemático Esteira Arduino**
![Esquemático Arduino](esquematico-arduino-esteira.png)
- **Descrição**: Esquemático completo da esteira transportadora
- **Componentes**: Arduino, motor NEMA17, driver A4988, sensores IR, LCD
- **Interface**: Controles manuais, display, emergência
- **Formato**: 1600x1100px PNG

#### **Esquemático Estação QC**
![Esquemático Raspberry Pi](esquematico-raspberry-qc.png)
- **Descrição**: Diagrama de conexões da estação de controle de qualidade
- **Componentes**: Raspberry Pi, câmera, LED ring, motor, controladores
- **Alimentação**: 12V/5V/3.3V distribution, power management
- **Formato**: 1600x1200px PNG

#### **Diagrama Sistema Integrado**
![Sistema Integrado](diagrama-sistema-integrado.png)
- **Descrição**: Integração global de todos os componentes
- **Rede**: WiFi, MQTT, comunicação entre dispositivos
- **Fluxo**: Da pesagem do filamento ao produto final
- **Formato**: 1800x1200px PNG

**Guia Técnico**: [GUIA-CONEXOES.md](GUIA-CONEXOES.md) - Instruções detalhadas de montagem

## 🎨 Diretrizes Visuais

### **Paleta de Cores**
- **Verde 3dPot**: `#2E8B57` - Identidade visual
- **Laranja Técnico**: `#FF6B35` - Destaques e alertas
- **Azul Tecnológico**: `#4A90E2` - Interfaces e dados
- **Roxo Avançado**: `#9C27B0` - Análise e AI
- **Background**: `#F8F9FA` - Base limpa
- **Texto**: `#2C3E50` - Leitura otimizada

### **Ícones e Símbolos**
- 🔧 Hardware e ferramentas
- 📡 Conectividade IoT
- 📊 Dashboards e dados
- 🏭 Processamento industrial
- 🎯 Precisão e qualidade
- 🚀 Automação e fluxo

### **Padrões de Design**
- **Bordas**: Arredondadas (8px)
- **Sombras**: Suaves (#00000020)
- **Tipografia**: Sans-serif, legível
- **Espaçamento**: Consistente e arejado
- **Alinhamento**: Grid responsivo
- **Estados**: Visual claro (ativo/inativo/erro)

## 📈 Casos de Uso da Galeria

### **Para Desenvolvedores**
- Compreensão rápida da arquitetura
- Guia de integração entre sistemas
- Referência para desenvolvimento
- Documentação técnica visual

### **Para Fabricantes**
- Especificações claras de modelos 3D
- Guia de montagem visual
- Material para marketing
- Apresentações para clientes

### **Para Comunidade**
- Showcase de projetos
- Material educativo
- Inspiração para novos projetos
- Documentação acessível

## 🔄 Próximas Expansões

### **Imagens Físicas** (Planejado)
- [ ] Fotos reais dos projetos montados
- [ ] Vídeos demonstrativos (GIFs)
- [ ] Time-lapse de montagem
- [ ] Vídeos de funcionamento

### **Interfaces Avançadas** (Planejado)
- [ ] Mockups mobile
- [ ] Prototipação interativa
- [ ] Animações de uso
- [ ] Comparações antes/depois

### **Documentação Visual** (Planejado)
- [ ] Diagramas de circuito
- [ ] Esquemáticos técnicos
- [ ] Fluxogramas de processo
- [ ] Infográficos de benefícios

## 📝 Atualizações

- **10 Nov 2025**: Galeria inicial criada com 7 diagramas técnicos
- **Futuro**: Expansão com fotos reais e vídeos demonstrativos

---

**Nota**: Todas as imagens estão em formato PNG otimizado para web e documentação. Os diagramas foram criados usando Mermaid para garantir consistência e escalabilidade.