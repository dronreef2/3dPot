# Guia de Instalação - Toolchain Open-Source

Este guia detalha a instalação e configuração de todo o toolchain necessário para os projetos do 3D Pot.

## 1. Modelagem 3D

### Tinkercad (Iniciantes)
```bash
# Acesso direto via navegador
# URL: https://www.tinkercad.com/
# Não requer instalação
```

### FreeCAD (Engenharia)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install freecad

# Windows
# Download: https://www.freecadweb.org/downloads.php

# macOS
brew install freecad
```

### OpenSCAD (Modelagem via Código)
```bash
# Ubuntu/Debian
sudo apt install openscad

# Windows
# Download: https://www.openscad.org/downloads.html

# macOS
brew install openscad
```

## 2. Fatiamento (Slicing)

### Ultimaker Cura
```bash
# Ubuntu/Debian
wget https://github.com/Ultimaker/Cura/releases/download/5.9.0/Ultimaker-Cura-5.9.0-linux-modern.AppImage
chmod +x Ultimaker-Cura-5.9.0-linux-modern.AppImage

# Windows/macOS: Download direto do site
# https://ultimaker.com/software/ultimaker-cura
```

### PrusaSlicer
```bash
# Ubuntu/Debian
wget https://github.com/prusa3d/PrusaSlicer/releases/download/version_2.8.1/PrusaSlicer-2.8.1+linux-x64-202407261536.tar.gz
tar -xzf PrusaSlicer-*.tar.gz
sudo mv PrusaSlicer-*/usr/local/bin/

# Windows/macOS: Download direto
# https://www.prusa3d.com/page/prusaslicer_424/
```

## 3. Programação de Hardware

### PlatformIO (VSCode Extension)

#### Instalação do VSCode
```bash
# Ubuntu/Debian
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Windows: Download do site oficial
# macOS: App Store ou download direto
```

#### Instalação da Extension PlatformIO
1. Abrir VSCode
2. Ir para Extensions (Ctrl+Shift+X)
3. Buscar "PlatformIO"
4. Instalar "PlatformIO IDE"

#### Configuração do Arduino
```bash
# Ubuntu/Debian
sudo apt install arduino

# Windows: Arduino IDE
# macOS: Arduino IDE
```

### Bibliotecas Necessárias

#### Para ESP32/ESP8266
```
# No PlatformIO, adicione ao platformio.ini:
lib_deps = 
    AsyncTCP
    ESPAsyncWebServer
    ArduinoJson
    HX711-library
    PubSubClient
```

#### Para Arduino
```
# Bibliotecas via Library Manager:
- AccelStepper
- Servo
- Wire
-EEPROM
```

#### Para Raspberry Pi
```bash
# Python packages
pip3 install opencv-python
pip3 install flask
pip3 install numpy
pip3 install RPi.GPIO
pip3 install picamera2
pip3 install paho-mqtt
```

## 4. Comunicação IoT

### Mosquitto MQTT Broker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Iniciar serviço
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Testar instalação
mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT"
mosquitto_sub -h localhost -t "test/topic"
```

### Node-RED
```bash
# Instalação via npm
npm install -g node-red

# Ou via script oficial
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Iniciar Node-RED
node-red

# Acessar: http://localhost:1880
```

## 5. Configuração de Rede

### WiFi para ESP32/ESP8266
```cpp
// Exemplo de configuração
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";

// Configurações avançadas
WiFi.mode(WIFI_STA);
WiFi.begin(ssid, password);
WiFi.setAutoReconnect(true);
WiFi.persistent(true);
```

### Rede Local para IoT
```bash
# Configurar IP estático (opcional)
# Editar /etc/dhcpcd.conf
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

## 6. Ferramentas de Desenvolvimento

### Git
```bash
# Ubuntu/Debian
sudo apt install git

# Configuração inicial
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

### SSH (para Raspberry Pi)
```bash
# No Raspberry Pi
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh

# Conexão remota
ssh pi@192.168.1.xxx
```

## 7. Verificação da Instalação

### Teste Arduino
```cpp
// Exemplo básico
void setup() {
    Serial.begin(9600);
    Serial.println("Arduino funcionando!");
}

void loop() {
    Serial.println("Teste");
    delay(1000);
}
```

### Teste ESP32
```cpp
#include <WiFi.h>

void setup() {
    Serial.begin(115200);
    WiFi.begin("SUA_REDE", "SUA_SENHA");
    Serial.println("Conectando WiFi...");
}
```

### Teste Raspberry Pi
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

try:
    while True:
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
```

## 8. Solução de Problemas

### Erros Comuns

#### ESP32 não conecta WiFi
- Verificar credenciais
- Verificar alimentação (pode precisar de fonte externa)
- Checar pinagem dos sensores

#### Arduino motor não gira
- Verificar alimentação do motor (12V separado)
- Verificar conexões do driver
- Checar se o código está carregado corretamente

#### Raspberry Pi câmera não funciona
```bash
# Verificar câmera
vcgencmd get_camera

# Habilitar câmera
sudo raspi-config
# Interface Options > Camera > Enable
```

#### OpenCV não instala
```bash
# Para problemas com OpenCV no Raspberry Pi
sudo apt update
sudo apt install libopencv-dev python3-opencv
pip3 install opencv-python --no-cache-dir
```

### Logs e Debug

#### ESP32/Arduino
```cpp
// Habilitar logs detalhados
#define DEBUG 1
#if DEBUG
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
#endif
```

#### Raspberry Pi
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/3dpot.log'),
        logging.StreamHandler()
    ]
)
```

## 9. Próximos Passos

Após a instalação completa:

1. **Teste cada componente** individualmente
2. **Configure a rede IoT** básica
3. **Imprima os modelos 3D** necessários
4. **Monte o hardware** seguindo os guias específicos
5. **Programe cada dispositivo**
6. **Integre tudo** via Node-RED

## Suporte

Para dúvidas e problemas:
- Documentação oficial de cada ferramenta
- Fóruns da comunidade Arduino/ESP32/Raspberry Pi
- GitHub Issues deste projeto
