# Sistema de Modelagem Inteligente 3D

## Visão Geral

O **Sistema de Modelagem Inteligente 3D** é uma solução completa que integra a API do Slant 3D com o projeto Central de Controle Inteligente 3dPot, permitindo criação automática de modelos 3D através de prompts inteligentes e análise inteligente de requisitos.

## Características Principais

### 🧠 Processamento Inteligente de Prompts
- Análise automática de intenção do usuário
- Detecção de tipo de projeto (estrutura, suporte, enclosure, central)
- Geração de sugestões baseadas em AI
- Recomendações de materiais e configurações

### 🎯 Integração Slant 3D API
- Conexão direta com API oficial Slant 3D
- Busca de filamentos disponíveis em tempo real
- Cálculo automático de custos
- Monitoramento de uso da API

### 💰 Calculadora de Orçamento
- Estimativas de custo em tempo real
- Múltiplas opções de materiais
- Análise de relação custo-benefício
- Ratings automáticos para cada opção

### 🔧 Configurações de Impressão
- Parâmetros otimizados por tipo de projeto
- Temperaturas automáticas baseadas no material
- Recomendações de velocidade e qualidade
- Configurações de suporte e preenchimento

### 🌐 Interface Web Responsiva
- Design moderno com Tailwind CSS
- Interface intuitiva para usuários
- Gráficos em tempo real
- Feedback visual imediato

## Arquitetura do Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Interface     │◄──►│  Servidor Flask  │◄──►│   Slant 3D      │
│      Web        │    │   Integração     │    │      API        │
│                 │    │                  │    │                 │
│ • Prompt Input  │    │ • API REST       │    │ • Filaments     │
│ • Análise       │    │ • Processamento  │    │ • Pricing       │
│ • Filtros       │    │ • Lógica AI      │    │ • Usage         │
│ • Orçamento     │    │ • Cache          │    │ • Authentication│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Modelos 3D     │    │  Dados Locais    │    │  Rate Limiting  │
│                 │    │                  │    │                 │
│ • OpenSCAD      │    │ • Cache API      │    │ • 100 req/min   │
│ • Validação     │    │ • Histórico      │    │ • Monitoramento │
│ • Exportação    │    │ • Configs        │    │ • Alertas       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Biblioteca Flask
- Conexão com internet
- API Key do Slant 3D

### Instalação Rápida
```bash
# 1. Clonar ou obter os arquivos do sistema
cd /workspace

# 2. Instalar dependências Python
pip install flask flask-cors requests

# 3. Configurar API Key (já configurada)
# API_KEY="sl-cc497e90df04027eed2468af328a2d00fa99ca5e3b57893394f6cd6012aba3d4"

# 4. Inicializar sistema
python slant3d_integration.py

# 5. Executar servidor web
python servidor_integracao.py
```

### Configuração de Ambiente
```bash
# Variáveis de ambiente opcionais
export PORT=5000                    # Porta do servidor (padrão: 5000)
export HOST=0.0.0.0                 # Host do servidor (padrão: 0.0.0.0)
export DEBUG=false                   # Modo debug (padrão: false)
export API_TIMEOUT=30               # Timeout para API calls
```

## Uso do Sistema

### 1. Interface Web Principal

Acesse `http://localhost:5000` para usar a interface web:

#### 🔮 Gerador de Prompts Inteligentes
- Insira uma descrição natural do modelo desejado
- Selecione tipo de projeto (protótipo/produção/estudo)
- Defina nível de complexidade
- Clique em "Processar Prompt Inteligente"

#### 🎯 Análise Automática
O sistema ira:
- Detectar tipo de objeto automaticamente
- Recomendar materiais apropriados
- Gerar sugestões técnicas
- Sugerir configurações de impressão

#### 🔍 Filtros de Material
- Filtrar por tipo (PLA/ABS/PETG)
- Filtrar por cor
- Definir preço máximo
- Buscar filamentos compatíveis

#### 💰 Calculadora de Orçamento
- Nome do modelo
- Volume estimado (cm³)
- Material preferido
- Cor preferida
- Cálculo automático com múltiplas opções

### 2. API REST Endpoints

#### Status da API
```http
GET /api/status
```
Retorna status da conexão com Slant 3D e uso atual.

#### Buscar Filamentos
```http
GET /api/filaments?material=PLA&color=branco&max_price=0.03
```
Busca filamentos com filtros opcionais.

#### Analisar Prompt
```http
POST /api/analyze-prompt
Content-Type: application/json

{
  "prompt": "criar suporte para arduino com ventilação",
  "project_type": "prototipo",
  "complexity": "media"
}
```
Análise inteligente de prompt do usuário.

#### Calcular Orçamento
```http
POST /api/calculate-budget
Content-Type: application/json

{
  "model_name": "Suporte Arduino V2",
  "volume": 45.5,
  "preferred_material": "PLA",
  "preferred_color": "branco"
}
```
Calcula orçamento completo com múltiplas opções.

### 3. Sistema Python Standalone

Uso direto do sistema Python:

```python
from slant3d_integration import ModelagemInteligente

# Inicializar sistema
sistema = ModelagemInteligente("sl-api-key-here")

# Processar prompt
resultado = sistema.processar_prompt(
    "criar chassi base para central de controle inteligente"
)

# Buscar filamentos PLA disponíveis
filamentos = sistema.api.filter_filaments({
    "type": "PLA",
    "available": True
})

# Calcular orçamento
orcamento = sistema.calcular_orçamento_completo(
    "Meu Modelo",
    volume_cm3=50.0,
    requisitos_filamento={"material": "PLA", "cor": "branco"}
)
```

## Exemplos de Prompts Inteligentes

### Projetos Estruturais
```
"criar chassi principal para central de controle com 6 compartimentos"
"base estrutural para estação de qualidade com suportes ajustáveis"
"gabinete resistente para Arduino e ESP32 com furos de ventilação"
```

### Suportes Específicos
```
"suporte para Raspberry Pi com encaixe preciso e furos M3"
"holder para sensor de peso HX711 com proteção contra vibrações"
"braço articulado para display touchscreen 7 polegadas"
```

### Enclosures Avançados
```
"caixa hermética para projeto central com tampa de acesso"
"gabinete com furos de ventilação e slots para cabos"
"enclosure com iluminação LED interna e janela transparente"
```

## Configurações de Impressão

### Por Tipo de Material

#### PLA
- **Temperatura extrusor**: 200-220°C
- **Temperatura mesa**: 60-70°C
- **Velocidade**: 50-60mm/s
- **Características**: Fácil impressão, boa precisão

#### ABS
- **Temperatura extrusor**: 240-260°C
- **Temperatura mesa**: 90-100°C
- **Velocidade**: 40-50mm/s
- **Características**: Alta resistência, resistente a impactos

#### PETG
- **Temperatura extrusor**: 220-240°C
- **Temperatura mesa**: 70-80°C
- **Velocidade**: 45-55mm/s
- **Características**: Transparência, resistência química

### Por Tipo de Projeto

#### Prototipagem
- **Preenchimento**: 15-20%
- **Altura de camada**: 0.25-0.3mm
- **Velocidade**: Alta (60-80mm/s)
- **Supports**: Mínimo necessário

#### Produção
- **Preenchimento**: 30-50%
- **Altura de camada**: 0.2-0.25mm
- **Velocidade**: Média (40-60mm/s)
- **Supports**: Automático

## Monitoramento e Logs

### Logs do Sistema
- Requisições HTTP
- Erros da API Slant 3D
- Processamento de prompts
- Cálculos de orçamento

### Métricas de Uso
- Requests por minuto
- Filamentos consultados
- Orçamentos calculados
- Status da API

### Alertas Automáticos
- Aproximação do limite de API
- Erros de conectividade
- Falhas na validação
- Timeout de requisições

## Integração com 3dPot

O sistema se integra perfeitamente com o projeto Central de Controle Inteligente 3dPot:

### Modelos 3D Validados
- **chassi-principal.scad**: Chassi base com 6 compartimentos
- **sistema-suportes-auxiliares.scad**: Sistema modular de suportes
- **suporte-arduino-esteira.scad**: Suporte específico Arduino
- **suporte-esp32-hx711.scad**: Suporte sensor de peso
- **suporte-fonte-conectores.scad**: Suporte alimentação
- **suporte-raspberry-pi-qc.scad**: Suporte estação QC

### Componentes Integrados
- **Arduino**: Controle de motores e sensores
- **ESP32**: Conectividade WiFi e Bluetooth
- **Raspberry Pi**: Processamento central
- **HX711**: Sensor de peso de alta precisão

### Workflow Completo
1. **Prompt**: Usuário descreve necessidade
2. **Análise**: Sistema detecta componentes necessários
3. **Materiais**: Filtra filamentos compatíveis
4. **Orçamento**: Calcula custos totais
5. **Impressão**: Gera G-code otimizado
6. **Montagem**: Integra com hardware existente
7. **Teste**: Validação funcional

## Troubleshooting

### Problemas Comuns

#### API Slant 3D não conecta
```
❌ Erro: "API não disponível"
✅ Solução: Verificar chave de API e conectividade
```

#### Filamentos não aparecem
```
❌ Erro: "Lista vazia de filamentos"
✅ Solução: Verificar filtros e disponibilidade
```

#### Cálculo de custo falhando
```
❌ Erro: "Filamento não encontrado"
✅ Solução: Verificar ID do filamento
```

#### Prompt não processa
```
❌ Erro: "Análise falhou"
✅ Solução: Verificar formato do prompt
```

### Logs de Debug
```bash
# Ativar modo debug
export DEBUG=true
python servidor_integracao.py

# Ver logs em tempo real
tail -f /var/log/modelagem-sistema.log
```

## Roadmap e Melhorias Futuras

### Próximas Versões
- [ ] **AI Generator**: Geração automática de código OpenSCAD
- [ ] **3D Preview**: Visualização 3D em tempo real
- [ ] **Cloud Storage**: Armazenamento de projetos na nuvem
- [ ] **Team Collaboration**: Compartilhamento entre equipes
- [ ] **Cost Optimization**: Otimização automática de custos
- [ ] **Material Science**: Base de dados de propriedades de materiais

### Integrações Planejadas
- [ ] **AutoCAD Fusion 360**: Importação de modelos CAD
- [ ] **PrusaSlicer**: Geração automática de G-code
- [ ] **Thingiverse**: Publicação automática
- [ ] **MongoDB**: Armazenamento de projetos
- [ ] **Telegram Bot**: Controle via bot
- [ ] **WhatsApp Business**: Notificações automáticas

## Suporte e Contato

### Documentação
- **README**: Este documento
- **API Docs**: `/api/docs` (quando disponível)
- **Examples**: Pasta `/examples/`
- **Tests**: Pasta `/tests/`

### Comunidade
- **GitHub**: Repositório do projeto
- **Issues**: Relatório de problemas
- **Discussions**: Discussões e melhorias
- **Wiki**: Documentação extendida

### Contribuição
1. Fork do repositório
2. Criar branch para feature
3. Implementar com testes
4. Enviar Pull Request
5. Code review

## Licença

Este projeto está sob licença MIT. Consulte o arquivo LICENSE para detalhes.

---

**Sistema de Modelagem Inteligente 3D** - Powered by Slant 3D API  
Central de Controle Inteligente 3dPot - Versão 1.0.0  
Data: 2025-11-10