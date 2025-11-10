# Galeria Visual - 3dPot Projetos

## 📋 Descrições Visuais para Criação de Screenshots

### 🔧 Projeto 1: Monitor de Filamento ESP32

**Screenshot da Interface Web:**
- **Layout**: Interface web limpa e responsiva
- **Cabeçalho**: "Monitor de Filamento - ESP32" com ícone WiFi
- **Painel Principal**: 
  - Peso Atual: 1,245g
  - Porcentagem Restante: 73%
  - Estimativa de Tempo: 2.3 horas
- **Gráfico**: Evolução do peso ao longo do tempo
- **Status**: Conectado | Última Medição: agora
- **Controles**: Botão "Calibrar" e "Alerta 20%"

**Componentes na Mesa:**
- ESP32 DevKit ao centro
- Célula de carga com carretel de PLA branco
- Protoboard com jumpers coloridos
- Notebook mostrando interface web

### 🚀 Projeto 2: Esteira Transportadora Arduino

**Foto da Montagem:**
- **Vista Superior**: Esteiras de borracha com rolos laterais
- **Motor**: NEMA17 fixo no lado esquerdo
- **Sensores**: 3 sensores IR posicionados na esteira
- **Painel de Controle**: Arduino Uno + potenciômetro + display LCD
- **LEDs**: Verde (ligado), Amarelo (objeto detectado), Vermelho (erro)
- **Objetos na Esteiras**: Peças PLA de diferentes cores

**Interface de Controle:**
- Display LCD mostrando: "Velocidade: 60%" e "Status: OPERACIONAL"
- Potenciômetro ajustado para velocidade
- Botão de emergência vermelho

### 🏭 Projeto 3: Estação QC Raspberry Pi

**Dashboard Web:**
- **Cabeçalho**: "Estação de Controle de Qualidade"
- **Status**: "APROVADO" em verde
- **Detalhes da Peça**: 
  - Nome: "Suporte ESP32"
  - Dimensões: 50x30x5mm
  - Tempo de Análise: 45s
  - Confiança: 98.7%
- **Imagens**: 8 fotos da peça em diferentes ângulos
- **Análise**: "Superfície lisa, sem defeitos, tolerância dentro da especificação"

**Setup Físico:**
- Raspberry Pi 4 com case ventilado
- Câmera Pi HQ apontando para a mesa rotativa
- LED ring ao redor da câmera
- Motor de passo rotacionando a plataforma
- Peça sendo fotografada
- Notebook mostrando dashboard

### 🎨 Modelos 3D Conceptuais

**Suporte Monitor ESP32:**
- Vista isométrica mostrando:
  - Base retangular com furos de fixação
  - Suporte diagonal para o ESP32
  - Abertura para sensor HX711
  - Ventilação superior
  - Dimensões: 80x60x40mm

**Rolo Esteira Arduino:**
- Vista técnica com cortes:
  - Rolamento interno Ø10mm
  - Furo central para eixo Ø8mm  
  - Ranhuras para correia Ø2mm
  - Dimensões externas Ø40x60mm
  - Material: PLA, camada 0.2mm

**Case Estação QC:**
- Vista explodida mostrando:
  - Base com ventiladores
  - Tampa com janela de vidro
  - Suportes internos para Raspberry Pi
  - Furos para cabos e conectores
  - Dimensões: 200x150x120mm

### 📊 Diagramas de Fluxo

**Fluxo Monitor Filamento:**
```
[Iniciar] → [Calibrar Peso Vazio] → [Monitorar Peso Atual] → [Calcular % Restante]
     ↓
[Enviar via WiFi] → [Interface Web] ← [Alertas: 20%, 10%, 5%]
     ↓
[Repetir a cada 30s]
```

**Fluxo Esteira Transportadora:**
```
[Iniciar Sistema] → [Ajustar Velocidade] → [Motor Acionado]
     ↓
[Sensores Detectam Objeto] → [Parar Motor] → [Processar Objeto]
     ↓
[Aguardar Retirada] → [Reiniciar Ciclo] ou [Modo Manual]
```

**Fluxo Estação QC:**
```
[Capturar Imagem 1] → [Análise OpenCV] → [Rotacionar Peça 45°]
     ↓
[Repetir 8x] → [Análise Comparativa] → [Gerar Relatório]
     ↓
[Dashboard: APROVADO/REPROVADO] → [Histórico]
```

### 🎯 Elementos Visuais Comuns

**Paleta de Cores:**
- Primária: #2E8B57 (Verde 3D Pot)
- Secundária: #FF6B35 (Laranja técnico)
- Accent: #4A90E2 (Azul tecnológico)
- Background: #F8F9FA (Cinza claro)
- Texto: #2C3E50 (Azul escuro)

**Ícones Técnicos:**
- WiFi: Conectividade ESP32
- Engrenagem: Controle Arduino
- Câmera: Visão Raspberry Pi
- 3D: Impressão e modelos
- Dashboard: Interface web

**Badges de Status:**
- ✅ OPERACIONAL
- ⚠️ ATENÇÃO
- ❌ ERRO
- 🔄 PROCESSANDO
- 📡 CONECTADO