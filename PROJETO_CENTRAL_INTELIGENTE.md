# 🏭 3dPot - Central de Controle Inteligente

## Visão Geral
Desenvolvimento de uma central de controle que integra todos os componentes existentes em um sistema completo de monitoramento de impressão 3D, controle de qualidade e automação de fluxo de trabalho.

## 🎯 Objetivos
- **Integração**: Unificar Arduino, ESP32 e Raspberry Pi em um sistema coeso
- **Automatização**: Automatizar fluxo completo de impressão 3D
- **Monitoramento**: Monitorar qualidade, peso do filamento e processo
- **Interface**: Interface web centralizada para controle de todos os sistemas
- **Protótipo**: Sistema físico funcional com peças impressas em 3D

## 🏗️ Arquitetura do Sistema

### Componentes Principais
```
Central de Controle Inteligente
├── 🏭 Esteirão de Alimentação (Arduino)
│   ├── Motor de passo NEMA17
│   ├── Sensores IR de detecção
│   ├── LEDs de status
│   └── Controle de velocidade
├── ⚖️ Monitor de Peso (ESP32)
│   ├── Sensor HX711 (balança)
│   ├── Conectividade WiFi
│   ├── Interface web
│   └── Monitoramento em tempo real
├── 📹 Estação de QC (Raspberry Pi)
│   ├── Câmera Pi HQ
│   ├── LEDs de iluminação
│   ├── Motor de passo para rotação
│   ├── Visão computacional
│   └── Análise de qualidade
├── 🖥️ Interface Central
│   ├── Dashboard unificado
│   ├── Controle de todos os módulos
│   ├── Logs e relatórios
│   └── API REST
└── 🏗️ Estrutura Mecânica
    ├── Chassi impresso em 3D
    ├── Suportes modulares
    ├── Cablagem organizada
    └── Expansibilidade
```

## 📋 Fases de Desenvolvimento

### Fase 1: Design e Modelagem 3D (1 semana)
**Objetivos:**
- Projetar chassi principal da central
- Criar suportes modulares para cada componente
- Desenvolver sistema de fixação para esteira
- Projetar case para eletrônica

**Peças 3D a Desenvolver:**
1. **Chassi Principal** (base da estação)
2. **Suporte ESP32** (com furação para sensor HX711)
3. **Suporte Arduino** (com ventilação)
4. **Suporte Raspberry Pi** (com acesso GPIO)
5. **Gabaritos** para montagem da esteira
6. **Cobertura** para proteção da eletrônica
7. **Tampa** com acesso para display
8. **Organizador** de cabos

### Fase 2: Desenvolvimento de Software Integrado (1 semana)
**Objetivos:**
- Criar API central para comunicação entre módulos
- Desenvolver dashboard unificado
- Implementar protocolos de comunicação
- Criar sistema de logs centralizado

**Funcionalidades:**
- Interface web responsiva
- Controle remoto de todos os sistemas
- Monitoramento em tempo real
- Alertas e notificações
- Histórico de operações

### Fase 3: Integração e Montagem (3-5 dias)
**Objetivos:**
- Montar estrutura física
- Integrar componentes eletrônicos
- Conectar sistemas de comunicação
- Testes de funcionalidade

**Atividades:**
- Montagem mecânica
- Instalação da eletrônica
- Configuração de rede
- Calibração de sensores
- Testes de integração

### Fase 4: Calibração e Validação (2-3 dias)
**Objetivos:**
- Calibrar sensores de peso
- Ajustar parâmetros de qualidade
- Validar fluxo de trabalho
- Documentar procedimentos

**Validações:**
- Precisão do sensor de peso
- Detecção de objetos na esteira
- Qualidade das imagens da câmera
- Latência da comunicação
- Confiabilidade do sistema

## 🔧 Especificações Técnicas

### Especificações Mecânicas
- **Dimensões**: 40cm x 30cm x 20cm (aprox.)
- **Material**: PLA/ABS impresso em 3D
- **Montagem**: Parafusos M3 e inserts
- **Carga máxima**: 3kg (carga da esteira)
- **Temperatura operacional**: 0-50°C

### Especificações Eletrônicas
- **Alimentação**: 12V/5V (adaptador de 60W)
- **Comunicação**: WiFi (ESP32) + USB (Arduino) + GPIO (RPi)
- **Sensores**: HX711, IR, câmera Pi HQ
- **Atuadores**: 3x motores de passo
- **Interface**: Display 7" touch (opcional)

### Especificações de Software
- **Backend**: Python/Flask + Node.js
- **Frontend**: React/Vue.js responsivo
- **Database**: SQLite local + backup na nuvem
- **API**: RESTful com WebSocket para tempo real
- **Logs**: Sistema centralizado de logging

## 💡 Funcionalidades Planejadas

### 🏭 Controle da Esteirão
- Iniciar/parar automaticamente baseada no peso do filamento
- Velocidade ajustável conforme tipo de material
- Contagem de peças processadas
- Parada de emergência

### ⚖️ Monitor de Peso
- Monitoramento contínuo do carretel de filamento
- Alerta de filamento baixo
- Cálculo de peças restantes
- Histórico de consumo

### 📹 Análise de Qualidade
- Inspeção automática de peças impressas
- Detecção de defeitos (warping, stringing, etc.)
- Classificação automática (A, B, C)
- Relatórios de qualidade

### 🖥️ Interface Central
- Dashboard unificado
- Controle de todos os sistemas
- Configurações avançadas
- Relatórios e analytics
- Alertas em tempo real

## 🛠️ Ferramentas e Recursos Necessários

### Ferramentas Open Source Existentes
- **OpenSCAD**: Modelagem 3D (já disponível)
- **Python**: Programação principal
- **OpenCV**: Visão computacional (já disponível)
- **Flask**: Web framework
- **Git**: Controle de versão
- **Docker**: Containerização (opcional)

### Ferramentas Adicionais Necessárias
- **KiCad**: Design de PCB (se necessário)
- **Fusion 360** ou **FreeCAD**: Modelagem 3D avançada
- **VS Code**: IDE de desenvolvimento
- **Postman**: Teste de APIs

### Componentes Físicos Adicionais
- Chassi de alumínio extrudado (20x20mm)
- Parafusos M3 e inserts
- Cabos JST e conectores
- Fita LED para iluminação
- Ventiladores 12V
- Dissipadores de calor

## 📊 Cronograma de Implementação

| Semana | Fase | Atividades Principais | Deliverables |
|--------|------|----------------------|--------------|
| 1 | Design 3D | Modelagem de todas as peças | Arquivos .scad e .stl |
| 2 | Software | Desenvolvimento da API e interface | Código funcional |
| 3 | Integração | Montagem física e eletrônica | Protótipo funcional |
| 4 | Validação | Testes e calibração | Sistema validado |

## 💰 Estimativa de Custos

### Componentes Eletrônicos (já possui)
- Arduino Uno: $15
- ESP32: $8
- Raspberry Pi 4: $35
- Motor NEMA17 x3: $45
- Sensor HX711: $5
- Câmera Pi HQ: $25
- **Subtotal**: $133

### Componentes Mecânicos e Extras
- Chassi de alumínio: $30
- Parafusos e inserts: $15
- Cabos e conectores: $20
- LEDs e ventiladores: $25
- Display 7" (opcional): $50
- **Subtotal**: $140

### Impressão 3D
- Filamento PLA: 2kg ($20)
- **Subtotal**: $20

**Total Estimado**: $293 (sem display) / $343 (com display)

## 🎯 Critérios de Sucesso

### Funcionalidade
- [ ] Integração completa entre todos os módulos
- [ ] Interface web responsiva e intuitiva
- [ ] Precisão do sensor de peso > 95%
- [ ] Detecção automática de qualidade > 90%
- [ ] Tempo de resposta < 2s para todos os controles

### Confiabilidade
- [ ] Sistema operacional contínuo por 24h
- [ ] Taxa de falhas < 1% em 100 ciclos
- [ ] Tolerância a falhas de rede
- [ ] Backup automático de dados

### Usabilidade
- [ ] Setup inicial em menos de 30 minutos
- [ ] Interface intuitiva para usuários não-técnicos
- [ ] Documentação completa
- [ ] Código bem documentado

## 🚀 Próximos Passos

### Imediato (Esta Semana)
1. **Finalizar design 3D** - Criar todas as peças necessárias
2. **Iniciar modelagem** - Desenvolver chassi e suportes
3. **Preparar código** - Estruturar repositório do novo projeto

### Curto Prazo (Próximas 2 Semanas)
1. **Imprimir primeiras peças** - Protótipo inicial
2. **Desenvolver interface** - Dashboard básico
3. **Integrar módulos** - Comunicação entre sistemas

### Médio Prazo (Próximo Mês)
1. **Testar protótipo completo** - Validação funcional
2. **Documentar procedimentos** - Guias de uso
3. **Preparar para deploy** - Versão final

---

**Objetivo**: Criar um sistema integrado, modular e escalável que demonstre o potencial completo do ecossistema 3dPot, servindo como referência para projetos futuros e solução comercial.

*Documento gerado em 2025-11-10 para o projeto 3dPot*