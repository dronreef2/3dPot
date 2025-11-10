# 🏭 3dPot - Manual de Montagem da Central de Controle Inteligente

## Visão Geral
Este manual fornece instruções detalhadas para a montagem da **Central de Controle Inteligente 3dPot**, que integra Arduino, ESP32, Raspberry Pi e componentes de automação em um sistema coeso.

## 📋 Lista de Materiais

### Peças 3D Necessárias
- **Chassi Principal** (1x): `chassi-principal.scad` → `.stl`
- **Suporte ESP32 + HX711** (1x): `suporte-esp32-hx711.scad` → `.stl`
- **Suporte Arduino** (1x): `suporte-arduino-esteira.scad` → `.stl`
- **Suporte Raspberry Pi** (1x): `suporte-raspberry-pi-qc.scad` → `.stl`
- **Suporte Fonte** (1x): `suporte-fonte-conectores.scad` → `.stl`
- **Plataforma Giratória QC** (1x): `sistema-suportes-auxiliares.scad` → `.stl`
- **Organizador de Cabos** (1x): Incluido no arquivo acima
- **Gabaritos de Montagem** (4x): Incluídos no arquivo acima

### Componentes Eletrônicos
- Arduino Uno/Nano (1x)
- ESP32 DevKit V1 (1x)
- Raspberry Pi 4 (1x)
- Motor de passo NEMA17 (3x)
- Sensor de peso HX711 (1x)
- Câmera Pi HQ (1x)
- Driver de motor A4988 (2x)
- LEDs: 3mm (4x cores diferentes)
- Botão de emergência (1x)
- Fonte 12V/5V 60W (1x)
- Ventiladores 12V (2x)

### Ferragens e Acessórios
- Parafusos M3 x 10mm (20x)
- Parafusos M3 x 20mm (10x)
- Parafusos M2 x 6mm (8x) - para eletrônica
- Inserts M3 roscados (16x)
- Insert M2 roscados (8x)
- Cabos JST-PH 2mm (10x)
- Terminais JST-PH (20x)
- Dissipadores de calor (para Raspberry Pi)
- Espuma anti-derrapante (pés)

### Ferramentas Necessárias
- Chave Phillips #1
- Chave Phillips #2
- Chave sextavada 2.5mm
- Multímetro
- Alicate de crimpagem JST
- Ferro de solda e estanho
- Cola quente (opcional)

## 🏗️ Instruções de Montagem

### Etapa 1: Preparação das Peças 3D

#### Impressão das Peças
**Configurações Recomendadas:**
- **Altura de camada**: 0.2mm
- **Infill**: 40%
- **Velocidade**: 50mm/s
- **Material**: PETG para peças mecânicas, PLA para gabaritos
- **Suporte**: Não necessário
- **Temperatura**: 220°C (PETG), 200°C (PLA)
- **Cama aquecida**: 70°C (PETG), 60°C (PLA)

#### Pós-processamento
1. **Remover resíduos** de impressão
2. **Lixar suavemente** as faces que farão contato
3. **Verificar furos** e desobstruir se necessário
4. **Instalar inserts** roscados (aquecer a 150°C e pressionar)
5. **Testar montagem** com parafusos

### Etapa 2: Montagem do Chassi Principal

1. **Posicionar chassi** sobre superfície plana
2. **Instalar pés** anti-derrapantes nos furos dos cantos
3. **Verificar nivelamento** usando nível
4. **Marcar posições** dos módulos com fita

### Etapa 3: Instalação do Suporte de Alimentação

1. **Posicionar fonte** no suporte específico
2. **Fixar fonte** com parafusos M3 x 6mm
3. **Instalar ventiladores** nos furos laterais
4. **Conectar cabos** da fonte ao distribuidor
5. **Testar funcionamento** da fonte (LED verde)

### Etapa 4: Instalação dos Módulos Eletrônicos

#### ESP32 + Monitor de Filamento
1. **Posicionar suporte** na localização indicada
2. **Fixar ESP32** nos pinos do suporte
3. **Instalar HX711** no suporte específico
4. **Conectar sensor de peso** ao HX711
5. **Conectar alimentação** do módulo distribuidor
6. **Configurar WiFi** (ver código)

#### Arduino + Controle de Esteirão
1. **Posicionar suporte** do Arduino
2. **Instalar botões** e LEDs de status
3. **Conectar motor de passo** ao driver
4. **Conectar sensores IR** nos furos designados
5. **Conectar alimentação** do módulo distribuidor
6. **Carregar sketch** do esteirão

#### Raspberry Pi + Estação QC
1. **Instalar dissipadores** no Pi
2. **Posicionar no suporte** específico
3. **Conectar câmera** nos furos apropriados
4. **Instalar motor de passo** para rotação
5. **Conectar LED ring** de iluminação
6. **Instalar ventilador** de resfriamento
7. **Conectar alimentação** do módulo distribuidor

### Etapa 5: Montagem da Plataforma Giratória

1. **Posicionar plataforma** sobre suporte do motor
2. **Alinhar eixo** central com eixo do motor
3. **Fixar plataforma** com parafusos M2
4. **Testar rotação** manual
5. **Instalar anéis** de rolamento se incluído

### Etapa 6: Organização de Cabos

1. **Usar organizador** de cabos na base
2. **Roteamento através** dos canais de cabos
3. **Fixar cabos** com abraçadeiras
4. **Conectar** todos os módulos
5. **Verificar tensão** dos cabos

### Etapa 7: Instalação de Gabaritos

1. **Posicionar gabaritos** sobre cada módulo
2. **Usar parafusos** de fixação M3
3. **Verificar alinhamento** de todos os componentes
4. **Testar acesso** a todos os conectores

### Etapa 8: Testes Iniciais

#### Teste de Alimentação
1. **Conectar fonte** à tomada
2. **Verificar LEDs** de status (todos devem acender)
3. **Medir tensões** com multímetro:
   - 12V ± 0.5V
   - 5V ± 0.2V
4. **Testar chave** liga/desliga

#### Teste de Comunicação
1. **Verificar WiFi** do ESP32
2. **Testar interface** web do ESP32
3. **Verificar GPIO** do Raspberry Pi
4. **Testar comunicação** serial do Arduino
5. **Verificar conectividade** entre módulos

#### Teste Mecânico
1. **Testar motores** de passo individualmente
2. **Verificar sensores** IR
3. **Testar rotação** da plataforma
4. **Verificar LEDs** de iluminação
5. **Testar botões** de controle

## 🔧 Configuração de Software

### ESP32 - Monitor de Filamento
```cpp
// Configurar WiFi no arquivo de configuração
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";

// Calibrar sensor HX711
float pesoCarretelVazio = 200.0;  // Ajustar conforme carretel
scale.set_scale(2280.0);  // Fator de escala
```

### Arduino - Controle de Esteirão
```cpp
// Configurar pinos conforme suporte
const int STEP_PIN = 2;
const int DIR_PIN = 3;
const int ENABLE_PIN = 4;
const int SENSOR_ENTRADA = 5;
const int SENSOR_SAIDA = 6;
const int BOTAO_ACIONAMENTO = 7;
```

### Raspberry Pi - Estação QC
```python
# Configurar câmera
config = {
    'width': 640,
    'height': 480,
    'fps': 30,
    'led_brightness': 100
}
```

### Interface Central
1. **Instalar dependências** Python
2. **Configurar rede** WiFi
3. **Iniciar servidor** Flask
4. **Acessar interface** web
5. **Configurar sensores** e calibrar

## 📱 Interface de Controle

### URL de Acesso
- **ESP32 Monitor**: `http://[IP_DO_ESP32]/`
- **Arduino Console**: Porta serial
- **RPi QC Station**: `http://[IP_DO_RPI]/qc`
- **Dashboard Central**: `http://[IP_PRINCIPAL]/dashboard`

### Funcionalidades da Interface
- **Monitor de Peso**: Visualização em tempo real
- **Controle da Esteheira**: Liga/desliga, velocidade
- **Estação QC**: Iniciar inspeção, visualizar resultados
- **Status Geral**: LEDs de todos os sistemas
- **Configurações**: Ajuste de parâmetros
- **Logs**: Histórico de operações

## 🔍 Troubleshooting

### Problemas Comuns

#### ESP32 não conecta ao WiFi
- **Verificar credenciais** na configuração
- **Verificar LED de status** do módulo
- **Resetar módulo** e reconfigurar

#### Arduino não responde
- **Verificar fonte** de alimentação
- **Verificar LEDs** de status
- **Testar comunicação** serial
- **Recompilar** e carregar firmware

#### Raspberry Pi não inicializa
- **Verificar alimentação** (5V, 2A mínimo)
- **Verificar cartão** SD
- **Verificar LEDs** de status
- **Testar com monitor** externo

#### Motores não giram
- **Verificar alimentação** de 12V
- **Verificar conexões** do driver
- **Testar driver** individualmente
- **Verificar código** de controle

#### Sensor de peso não funciona
- **Verificar conexões** HX711
- **Calibrar sensor** com peso conhecido
- **Verificar fonte** de alimentação do sensor
- **Testar comunicação** I2C

### LEDs de Status
- **Verde**: Sistema funcionando normalmente
- **Amarelo**: Sistema em operação (projeto rodando)
- **Vermelho**: Erro ou problema detectado
- **Azul**: Aguardando comando

## 📊 Manutenção

### Limpeza
- **Remover poeira** semanalmente
- **Limpar câmera** com pano macio
- **Verificar conexões** mensalmente
- **Lubricar** eixos dos motores (se necessário)

### Calibração
- **Sensor de peso**: Mensal ou quando houver deriva
- **Câmera**: Verificar foco e iluminação
- **Motores**: Verificar step e direção

### Backup
- **Configurações**: Fazer backup dos arquivos de config
- **Logs**: Exportar logs para análise
- **Firmware**: Manter versões de backup

## 🛡️ Segurança

### Medidas de Segurança
- **Verificar polaridade** antes de conectar
- **Usar fonte** adequada (12V/5V, 60W)
- **Instalar fusível** na entrada de energia
- **Botão de emergência** sempre acessível
- **Aterramento** adequado

### Procedimentos de Emergência
1. **Pressionar botão** de emergência
2. **Desconectar fonte** de energia
3. **Verificar causa** do problema
4. **Documentar** o incidente
5. **Testar sistema** antes de reiniciar

## 📞 Suporte

### Para Dúvidas Técnicas
- **Verificar logs** do sistema
- **Consultar documentação** do código
- **Testar componentes** individualmente
- **Verificar conexões** físicas

### Para Reportar Problemas
- **Documentar** passos para reproduzir
- **Capturar screenshots** da interface
- **Exportar logs** do sistema
- **Identificar** versão do firmware

## 📈 Expansões Futuras

### Funcionalidades Planejadas
- **Display LCD** para status local
- **Impressora térmica** para etiquetas
- **Banco de dados** para histórico
- **API REST** para integração
- **Aplicativo móvel** para controle remoto
- **Sensor de temperatura** ambiente
- **Alertas por email**/SMS

### Melhorias Mecânicas
- **Câmbio automático** de carretel
- **Sistema de limpeza** da plataforma
- **Iluminação LED** programável
- **Gaveta** para armazenamento
- **Roda de transporte** para mobilidade

---

**Este manual é um guia vivo que será atualizado conforme melhorias sejam implementadas no projeto 3dPot.**

*Versão 1.0 - Gerado em 2025-11-10*