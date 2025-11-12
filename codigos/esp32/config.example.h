/*
 * 3dPot ESP32 Monitor - Template de Configuração
 * 
 * INSTRUÇÕES:
 * 1. Copie este arquivo para 'config.h'
 * 2. Ajuste as configurações abaixo com seus valores reais
 * 3. NUNCA comite o arquivo config.h no git
 */

#ifndef CONFIG_H
#define CONFIG_H

// ================================
// REDE WI-FI
// ================================
// Credenciais da sua rede WiFi
#define WIFI_SSID "SUA_REDE_WIFI"
#define WIFI_PASSWORD "SUA_SENHA_WIFI"

// ================================
// MODO ACCESS POINT (fallback)
// ================================
// Caso não consiga conectar ao WiFi, cria access point
#define AP_SSID "3dPot-Monitor"
#define AP_PASSWORD "12345678"  // Mínimo 8 caracteres
#define AP_CHANNEL 1

// ================================
// CONEXÃO MQTT (para centralização)
// ================================
// Endereço do broker MQTT (opcional)
#define MQTT_ENABLE false
#define MQTT_SERVER "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USER ""  // Leave empty if no auth
#define MQTT_PASSWORD ""
#define MQTT_TOPIC_PREFIX "3dpot/esp32"

// ================================
// SENSOR DE PESO (HX711)
// ================================
// Pinos conectados ao HX711
#define HX711_DOUT_PIN 4
#define HX711_SCK_PIN 5
#define HX711_GAIN 128  // Usually 128

// Calibração do sensor (ajuste conforme sua balança)
#define HX711_SCALE_FACTOR 2280.0
#define WEIGHT_OFFSET_TOLERANCE 0.1  // kg

// ================================
// CONFIGURAÇÕES DE PESOS
// ================================
// Pesos em GRAMAS
#define CARRETEL_VAZIO_PESO_G 200.0      // Peso do carretel vazio
#define FILAMENTO_MAXIMO_G 1000.0        // Capacidade máxima do carretel
#define ALERTA_CRITICO_PERCENT 10.0      // Alerta crítico quando < X%
#define ALERTA_BAIXO_PERCENT 25.0        // Alerta baixo quando < X%

// ================================
// HARDWARE
// ================================
// Pinos de LEDs e botões
#define LED_STATUS_PIN 2
#define LED_WIFI_PIN 4
#define BUTTON_CALIBRATE_PIN 0  // GPIO0 (boot button)

// ================================
// SERVIDOR WEB
// ================================
// Configurações do servidor HTTP integrado
#define HTTP_SERVER_PORT 80
#define API_UPDATE_INTERVAL_MS 5000  // 5 segundos
#define CALIBRATION_SAMPLES 10       // Número de amostras para calibração

// ================================
// OVER-THE-AIR (OTA) UPDATES
// ================================
// Configurações para atualizações OTA (opcional)
#define OTA_ENABLE true
#define OTA_PASSWORD "admin"
#define OTA_HOSTNAME "3dpot-monitor"

// ================================
// CONFIGURAÇÕES AVANÇADAS
// ================================
// Timeout para conexões WiFi (milliseconds)
#define WIFI_TIMEOUT_MS 30000
// Número de tentativas de reconexão
#define WIFI_RECONNECT_ATTEMPTS 3
// Intervalo entre tentativas de reconexão (seconds)
#define WIFI_RECONNECT_INTERVAL 30

// Habilitar debug serial
#define DEBUG_SERIAL true
#define DEBUG_SERIAL_BAUDRATE 115200

#endif // CONFIG_H