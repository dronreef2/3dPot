# 🔌 Guia Técnico de Conexões - Projetos 3dPot

Este guia contém os diagramas esquemáticos e instruções de conexão para montagem física dos três projetos do ecossistema 3dPot.

## 📁 Arquivos de Diagramas

```
assets/screenshots/
├── esquematico-esp32-monitor.png      # Conexões ESP32 + HX711
├── esquematico-arduino-esteira.png    # Conexões Arduino + Motores
├── esquematico-raspberry-qc.png       # Conexões Raspberry Pi + Visão
├── diagrama-sistema-integrado.png     # Integração global do sistema
└── GUIA-CONEXOES.md                   # Este arquivo - instruções
```

## 🔧 Projeto 1: Monitor de Filamento ESP32

### Componentes Principais
- **ESP32 DevKit** (controlador principal)
- **Sensor HX711** (amplificador de célula de carga)
- **4x Células de carga** (sistema de pesagem)
- **LED de status** (indicador visual)
- **Alimentação**: 5V via USB

### Mapa de Conexões
```
ESP32                    HX711                  Células de Carga
GPIO 4  <---------------> DOUT                   Célula 1,2,3,4
GPIO 5  <---------------> SCK                    (Ponte de Wheatstone)
3.3V    <---------------> VCC                    Pontes
GND     <---------------> GND                    Paralelas
GPIO 2  <---------------> LED Status (via 220Ω)  Através de 4 fios
```

### Passos de Montagem
1. **Conectar HX711 ao ESP32**
   - DOUT → GPIO 4
   - SCK → GPIO 5  
   - VCC → 3.3V
   - GND → GND

2. **Instalar células de carga**
   - 4 células formando ponte
   - Cabos E+/E- (alimentação)
   - Cabos A+/A- (sinal)
   - Montar em suporte metálico

3. **Adicionar LED de status**
   - Anodo → GPIO 2 (via resistor 220Ω)
   - Catodo → GND

### Código de Cores Recomendado
- **Vermelho**: 3.3V/5V
- **Preto**: GND
- **Verde**: Sinais digitais
- **Azul**: Comunicação serial
- **Amarelo**: Controles

---

## 🚀 Projeto 2: Esteira Transportadora Arduino

### Componentes Principais
- **Arduino Uno/Nano** (controlador)
- **Motor NEMA17** (movimento da esteira)
- **Driver A4988** (controle de passo)
- **2x Sensores IR** (detecção de objetos)
- **Display LCD 16x2** (interface local)
- **Controles manuais** (potenciômetro, botões)

### Mapa de Conexões
```
Arduino                  Componente
Pin 2   <---------------> Sensor IR 1 (Detecção)
Pin 3   <---------------> Sensor IR 2 (Fim)
Pin 4   <---------------> A4988 STEP
Pin 5   <---------------> A4988 DIR
Pin 6   <---------------> Botão Emergência
Pin 7   <---------------> LED Status
Pin 8   <---------------> LCD RS
Pin 9   <---------------> LCD Enable
Pin 10  <---------------> LCD D4
Pin 11  <---------------> LCD D5
Pin 12  <---------------> LCD D6
Pin 13  <---------------> LCD D7
A0      <---------------> Potenciômetro (Velocidade)
5V      <---------------> VCC (Sensores, LCD)
GND     <---------------> GND (Todos)
```

### Alimentação Externa
- **Motor**: 12V 2A (NEMA17)
- **Lógica**: 5V (Arduino)
- **Driver**: 5V + 12V separados

### Configuração A4988
- **MS1/MS2/MS3**: GND (full step)
- **ENABLE**: GND (habilitado)
- **RESET**: +5V (ativo)

---

## 🏭 Projeto 3: Estação QC Raspberry Pi

### Componentes Principais
- **Raspberry Pi 4** (computador principal)
- **Camera Pi HQ** (captura de imagens)
- **LED Ring 12V** (iluminação controlada)
- **Motor NEMA17** (rotação da peça)
- **Controller A4988** (controle de passo)
- **Display OLED** (interface local - opcional)

### Mapa de Conexões GPIO
```
Raspberry Pi 4          Componente
GPIO 2  <---------------> A4988 STEP
GPIO 3  <---------------> A4988 DIR
GPIO 4  <---------------> LED Ring (PWM)
GPIO 17 <---------------> A4988 ENABLE
GPIO 22 <---------------> Buzzer/Alarm
GPIO 18 <---------------> Button (中断)
3.3V    <---------------> Pull-ups
5V      <---------------> Sensores, display
GND     <---------------> GND (compartilhado)
CSI-0   <---------------> Camera Pi HQ
I2C     <---------------> Display OLED (se houver)
```

### Interface de Alimentação
```
Fonte 12V 5A  <-----> LED Ring (12V)
             <-----> Motor NEMA17
             <-----> Controller A4988 VCC

Fonte 5V 3A   <-----> Raspberry Pi
             <-----> Controller A4988
             <-----> Display OLED

Fonte 3.3V   <-----> Pull-ups GPIO
```

### Configuração de Hardware
1. **Habilitar Câmera**
   ```bash
   sudo raspi-config
   # Interface Options > Camera > Enable
   ```

2. **Instalar Bibliotecas**
   ```bash
   pip install opencv-python RPi.GPIO adafruit-circuitpython-ina219
   ```

---

## 🌐 Integração do Sistema

### Rede WiFi Local
- **Router** como ponto central
- **DHCP** para automática de IPs
- **MQTT Broker** para comunicação

### Protocolo de Comunicação
- **MQTT Topics**:
  - `3dpot/filament/status` (peso, % restante)
  - `3dpot/conveyor/status` (velocidade, objetos)
  - `3dpot/qc/status` (resultado análise, tempo)

### Dashboard Central
- **Web Interface** unificada
- **Real-time updates** via WebSocket
- **Histórico de dados** em banco SQLite

---

## ⚡ Considerações de Alimentação

### Distância de Cabos
- **Power**: Máximo 2m (Queda de tensão)
- **Sinais**: Máximo 5m (Interferência)
- **UART**: Máximo 15m (baud rates baixos)
- **I2C**: Máximo 1m (cristalization)

### Filtragem de Alimentação
- **Capacitores 100µF** próximos aos componentes
- **Capacitores 0.1µF** para alta frequência
- **Indutores 10µH** para supressão EMI

### Proteção
- **Fusíveis** 5V: 1A, 12V: 2A
- **Diodos Zener** para proteção transientes
- **Resistores pull-up** para entradas

---

## 🔧 Ferramentas Necessárias

### Multímetro
- Verificar continuidade
- Medir tensões
- Testar resistências

### Ferro de Solda
- 40-60W com controle de temperatura
- Solda 60/40 ou 63/37
- Fluxo de solda

### Ferramentas
- Alicate descascador de fios
- Parafusos e porcas M2.5/M3
- Protoboard ou PCB
- Cabos jumper

### Software
- **Arduino IDE** para ESP32/Arduino
- **Visual Studio Code** com PlatformIO
- **Raspbian** no Raspberry Pi
- **KiCad** para projetos de PCB (futuro)

---

## 📋 Checklist de Montagem

### Pré-requisitos
- [ ] Todos os componentes disponíveis
- [ ] Ferramentas organizadas
- [ ] Ambiente de trabalho limpo
- [ ] Verificação de alimentação

### Montagem ESP32
- [ ] Teste da célula de carga
- [ ] Calibração inicial
- [ ] Interface web funcional
- [ ] Conectividade WiFi

### Montagem Arduino
- [ ] Teste do motor sem carga
- [ ] Calibração dos sensores IR
- [ ] Interface LCD funcionando
- [ ] Controle manual responsivo

### Montagem Raspberry Pi
- [ ] Câmera funcionando
- [ ] LED Ring calibrado
- [ ] Motor com controle preciso
- [ ] Dashboard web acessível

### Integração
- [ ] Rede WiFi estável
- [ ] MQTT broker rodando
- [ ] Dashboard central funcional
- [ ] Teste end-to-end

---

## 🚨 Problemas Comuns e Soluções

### Interferência Elétrica
- **Problema**: Valores instáveis nos sensores
- **Solução**: Separar linhas de power e sinal, usar cabos blindados

### Falha de Comunicação
- **Problema**: MQTT timeout ou desconnect
- **Solução**: Verificar rede WiFi, aumentar timeouts

### Motor Irregular
- **Problema**: Motor pulando passos
- **Solução**: Verificar alimentação, reduzir velocidade

### LED Ring Flicker
- **Problema**: Iluminação instável
- **Solução**: Verificar alimentção 12V, capacitor de filtragem

---

**Data de Criação**: 2025-11-10 09:08:50  
**Versão**: 1.0  
**Responsável**: MiniMax Agent