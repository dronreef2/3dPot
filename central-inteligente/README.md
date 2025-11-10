# 🏭 3dPot - Central de Controle Inteligente

## Descrição
Sistema integrado que combina Arduino, ESP32 e Raspberry Pi em uma central de controle inteligente para automação de impressão 3D, monitoramento de qualidade e controle de fluxo de produção.

## Características Principais
- **Monitoramento de Filamento**: Sensor de peso HX711 com alertas automáticos
- **Controle de Esteira**: Motor de passo com velocidade ajustável
- **Estação de QC**: Análise visual automática com câmera
- **Interface Web**: Dashboard responsivo em tempo real
- **Sistema Modular**: Componentes independentes e expansíveis
- **Banco de Dados**: Logs e histórico de operações
- **Alertas Automáticos**: Notificações de problemas do sistema

## Arquitetura do Sistema

```
Central de Controle 3dPot
├── ESP32 (Monitor de Filamento)
│   ├── Sensor HX711 (balança)
│   ├── WiFi + Web Server
│   └── API REST
├── Arduino (Controle de Esteira)
│   ├── Motor NEMA17
│   ├── Sensores IR
│   ├── LEDs de status
│   └── Comunicação serial
├── Raspberry Pi (Estação QC)
│   ├── Câmera Pi HQ
│   ├── Motor de passo
│   ├── LEDs de iluminação
│   └── Visão computacional
└── Interface Central
    ├── Flask + SocketIO
    ├── Dashboard web responsivo
    ├── Banco SQLite
    └── API unificada
```

## Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Instalação Automática
```bash
# Clone o repositório
git clone https://github.com/dronreef2/3dPot.git
cd 3dPot/central-inteligente

# Execute o script de instalação
chmod +x setup.sh
./setup.sh
```

### Instalação Manual
```bash
# Instalar dependências Python
pip install -r requirements.txt

# Configurar permissões
sudo usermod -a -G dialout $USER

# Reiniciar para aplicar permissões
sudo reboot
```

### Configuração
1. **Copie o arquivo de configuração**:
   ```bash
   cp config.json.example config.json
   ```

2. **Edite as configurações** em `config.json`:
   ```json
   {
     "esp32": {
       "url": "http://192.168.1.100"
     },
     "rpi_qc": {
       "url": "http://192.168.1.101"
     },
     "arduino": {
       "port": "/dev/ttyUSB0"
     }
   }
   ```

3. **Configure o WiFi do ESP32** no código fonte

## Uso

### Iniciar o Sistema
```bash
# Iniciar a central de controle
python central_control.py
```

A interface estará disponível em: `http://localhost:5000`

### API Endpoints

#### Status do Sistema
```http
GET /api/status
```

#### Controlar Produção
```http
POST /api/start_production
POST /api/stop_production
```

#### Controle de Qualidade
```http
POST /api/start_qc
```

#### Velocidade da Esteira
```http
GET /api/conveyor/speed
POST /api/conveyor/speed
```

#### Status dos Módulos
```http
GET /api/esp32/status
GET /api/rpiqc/status
```

#### Logs e Alertas
```http
GET /api/logs?limit=100
GET /api/alerts?resolved=false&limit=50
```

## Montagem

### Peças 3D Necessárias
1. **Chassi Principal** (300x200x15mm)
2. **Suporte ESP32 + HX711** (40x35x5mm)
3. **Suporte Arduino** (50x35x8mm)
4. **Suporte Raspberry Pi** (80x80x10mm)
5. **Suporte Fonte** (100x60x8mm)
6. **Plataforma Giratória** (60x60x5mm)
7. **Organizador de Cabos**

### Configurações de Impressão
- **Altura de camada**: 0.2mm
- **Infill**: 40%
- **Material**: PETG para peças mecânicas
- **Suporte**: Não necessário
- **Velocidade**: 50mm/s

### Componentes Eletrônicos
- Arduino Uno/Nano
- ESP32 DevKit V1
- Raspberry Pi 4
- Motor NEMA17 (3x)
- Sensor HX711
- Câmera Pi HQ
- LEDs 3mm
- Fonte 12V/5V 60W

Consulte o `MANUAL-MONTAGEM.md` para instruções detalhadas.

## Desenvolvimento

### Estrutura do Projeto
```
central-inteligente/
├── central_control.py      # Sistema principal
├── config.json             # Configurações
├── requirements.txt        # Dependências Python
├── setup.sh               # Script de instalação
├── templates/
│   └── dashboard.html     # Interface web
├── static/                # Arquivos estáticos
└── models/               # Modelos 3D
```

### Código Principal
- `CentralControlSystem`: Classe principal do sistema
- `central_control.py`: Servidor Flask + SocketIO
- `dashboard.html`: Interface web responsiva

### Banco de Dados
- **operation_logs**: Log de todas as operações
- **system_config**: Configurações do sistema
- **alerts**: Alertas e notificações

## Monitoramento

### Logs
- Arquivo: `central_control.log`
- Nivel: INFO, WARNING, ERROR
- Rotação automática

### Interface Web
- Dashboard em tempo real
- Status de todos os sistemas
- Controles de produção
- Histórico de operações

### Alertas
- Filamento baixo (100g mínimo)
- Erros de comunicação
- Falhas de sistema
- Status de conexões

## Troubleshooting

### ESP32 não conecta
1. Verificar WiFi no código
2. Verificar IP no config.json
3. Resetar ESP32
4. Verificar LEDs de status

### Arduino não responde
1. Verificar porta USB
2. Verificar velocidade (9600)
3. Verificar fonte de alimentação
4. Testar comunicação serial

### RPi QC não funciona
1. Verificar IP no config.json
2. Verificar câmera conectada
3. Verificar GPIO
4. Verificar LEDs de iluminação

### Banco de dados
```bash
# Resetar banco de dados
rm central_control.db
python central_control.py
```

## Expansões Futuras

### Funcionalidades Planejadas
- [ ] Display LCD local
- [ ] Impressora térmica
- [ ] Banco de dados na nuvem
- [ ] API para terceiros
- [ ] Aplicativo móvel
- [ ] Sensor de temperatura
- [ ] Alertas por email

### Melhorias Técnicas
- [ ] Docker container
- [ ] Kubernetes deployment
- [ ] SSL/HTTPS
- [ ] Autenticação
- [ ] Backup automático
- [ ] Análise de dados

## Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

- **Documentação**: Consulte `MANUAL-MONTAGEM.md`
- **Issues**: Reporte problemas no GitHub
- **Wiki**: Documentação adicional
- **Discussions**: Discuta melhorias

## Créditos

Desenvolvido como parte do projeto 3dPot - Sistema de Monitoramento e Automação para Impressão 3D.

---

**Versão**: 1.0.0  
**Data**: 2025-11-10  
**Autor**: MiniMax Agent