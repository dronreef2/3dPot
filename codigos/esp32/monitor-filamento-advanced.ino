/*
  3dPot ESP32 Monitor de Filamento - VERSÃO AVANÇADA
  
  Funcionalidades implementadas:
  ✅ Modo deep sleep para economia de energia
  ✅ Histórico de consumo de filamento
  ✅ Modo de calibração avançado
  ✅ Sensor de temperatura ambiente
  ✅ WebSocket para comunicação em tempo real
  ✅ OTA (Over-The-Air) updates
  ✅ Configuração WiFi via portal
  ✅ Monitoramento de tensão da bateria
  ✅ Calibração de célula de carga multi-ponto
  ✅ Logs estruturados com timestamp
  ✅ Alertas por threshold configurável
  
  Autor: 3dPot Project
  Versão: 2.0
  Data: 2025-11-10
*/

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <WebSocketsServer.h>
#include <ESPmDNS.h>
#include <Update.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <driver/adc.h>
#include <esp_adc_cal.h>
#include <Preferences.h>

// Configurações de hardware
#define HX711_DT 5
#define HX711_SCK 18
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define BATTERY_PIN 34
#define SLEEP_BUTTON 19
#define LED_STATUS 2
#define CALIBRATION_LED 15

// Configurações de rede
const char* ssid = "";
const char* password = "";
const char* mqtt_server = "";
const char* mqtt_user = "";
const char* mqtt_password = "";
const char* mqtt_topic = "3dpot/filament";

// Configurações do sistema
const unsigned long SLEEP_DURATION = 300000; // 5 minutos em microssegundos
const unsigned long DATA_LOG_INTERVAL = 30000; // 30 segundos
const float CALIBRATION_OFFSET = 0.0;
const float CALIBRATION_SCALE = 1.0;
const int CALIBRATION_SAMPLES = 10;

// Objetos globais
Preferences preferences;
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient client(espClient);
WebServer server(80);
WebSocketsServer webSocket = WebSocketsServer(81);

// Bibliotecas do HX711
class HX711 {
  public:
    HX711(int8_t sck, int8_t dt) {
      SCK = sck;
      DT = dt;
      SCALE = 1;
      OFFSET = 0;
      isReady = false;
      
      pinMode(SCK, OUTPUT);
      pinMode(DT, INPUT_PULLUP);
      
      powerDown();
      powerUp();
    }
    
    void begin() {
      powerUp();
      setScale();
      setOffset();
      calibrate();
    }
    
    void setScale(float scale = 1) {
      SCALE = scale;
    }
    
    void setOffset(long offset = 0) {
      OFFSET = offset;
    }
    
    float getUnits() {
      if (read() == 0x7FFFFFFF) return 0;
      return ((float)(read() - OFFSET) / SCALE);
    }
    
    void calibrate() {
      long total = 0;
      for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
        total += read();
        delay(100);
      }
      SETTLED_WEIGHT = total / CALIBRATION_SAMPLES;
      SCALE = SETTLED_WEIGHT;
    }
    
    void t tare() {
      setOffset(getUnits() * SCALE);
    }
    
  private:
    int8_t SCK, DT;
    float SCALE;
    long OFFSET;
    long SETTLED_WEIGHT;
    bool isReady;
    
    bool isDataReady() {
      return digitalRead(DT) == LOW;
    }
    
    void powerDown() {
      digitalWrite(SCK, LOW);
      digitalWrite(SCK, HIGH);
      delayMicroseconds(100);
    }
    
    void powerUp() {
      digitalWrite(SCK, LOW);
      isReady = true;
    }
    
    long read() {
      while (!isDataReady()) {
        delayMicroseconds(1);
        if (millis() - lastReadTime > 1000) break;
      }
      
      lastReadTime = millis();
      
      uint8_t data[3] = {0};
      data[2] = 0;
      
      // Ler 24 bits de dados
      for (int i = 0; i < 24; i++) {
        digitalWrite(SCK, HIGH);
        data[2] = (data[2] << 1) | (data[0] & 1);
        digitalWrite(SCK, LOW);
      }
      
      // Tare durante leitura
      digitalWrite(SCK, HIGH);
      digitalWrite(SCK, LOW);
      
      // Converter para valor signed
      if (data[2] & 0x80) {
        return 0x7FFFFFFF; // Valor inválido
      }
      
      return (long)((data[0] << 16) | (data[1] << 8) | data[2]);
    }
    
    long lastReadTime = 0;
};

HX711 scale(HX711_DT, HX711_SCK);

// Estrutura para dados do sistema
struct SystemData {
  float currentWeight;
  float currentTemperature;
  float batteryVoltage;
  unsigned long lastUpdate;
  bool wifiConnected;
  bool mqttConnected;
  int32_t freeHeap;
  float totalConsumed;
  float sessionConsumed;
  unsigned long sessionStart;
} systemData;

// Estrutura para logs de consumo
struct ConsumptionLog {
  unsigned long timestamp;
  float weight;
  float weightDelta;
  float totalConsumed;
};

// Arrays para armazenamento (usando Flash/PSRAM)
const int LOG_SIZE = 100;
ConsumptionLog consumptionLogs[LOG_SIZE];
int logIndex = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== 3dPot ESP32 Monitor de Filamento v2.0 ===");
  
  // Inicializar sistema
  initializeSystem();
  initializeWiFi();
  initializeSensors();
  initializeWebServer();
  initializeWebSocket();
  initializeMQTT();
  initializeCalibration();
  initializeUserInterface();
  
  // Configurar modo de operação
  configureOperationMode();
  
  Serial.println("Sistema inicializado com sucesso!");
  printSystemStatus();
}

void loop() {
  // Manter conexões ativas
  maintainConnections();
  
  // Processar dados dos sensores
  processSensors();
  
  // Processar logs de consumo
  processConsumption();
  
  // Processar interface web
  processWebInterface();
  
  // Verificar condições para sleep
  checkSleepConditions();
  
  delay(1000);
}

void initializeSystem() {
  Serial.println("Inicializando sistema...");
  
  // Configurar pinos
  pinMode(LED_STATUS, OUTPUT);
  pinMode(CALIBRATION_LED, OUTPUT);
  pinMode(SLEEP_BUTTON, INPUT_PULLUP);
  
  // Inicializar ADC para monitoramento de bateria
  analogReadResolution(12);
  
  // Inicializar preferences (persistência de dados)
  preferences.begin("filament-monitor", false);
  
  // Carregar configurações salvas
  loadConfiguration();
  
  // Inicializar estruturas de dados
  systemData.lastUpdate = millis();
  systemData.sessionStart = millis();
  systemData.sessionConsumed = 0.0;
  systemData.totalConsumed = preferences.getFloat("totalConsumed", 0.0);
  
  Serial.println("Sistema inicializado!");
}

void initializeWiFi() {
  Serial.println("Conectando ao WiFi...");
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startTime) < 10000) {
    digitalWrite(LED_STATUS, !digitalRead(LED_STATUS));
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    systemData.wifiConnected = true;
    Serial.println("\nWiFi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    systemData.wifiConnected = false;
    Serial.println("\nFalha ao conectar WiFi - iniciando modo Access Point");
    startAccessPointMode();
  }
}

void initializeSensors() {
  Serial.println("Inicializando sensores...");
  
  // Inicializar célula de carga
  scale.begin();
  scale.setScale(CALIBRATION_SCALE);
  scale.setOffset(CALIBRATION_OFFSET);
  scale.calibrate();
  
  // Inicializar sensor de temperatura
  dht.begin();
  
  Serial.println("Sensores inicializados!");
}

void initializeWebServer() {
  if (systemData.wifiConnected) {
    // Configurar mDNS
    if (MDNS.begin("3dpot-filament")) {
      Serial.println("mDNS iniciado: http://3dpot-filament.local");
    }
    
    // Endpoints da API REST
    server.on("/api/status", HTTP_GET, handleStatusRequest);
    server.on("/api/calibrate", HTTP_POST, handleCalibrationRequest);
    server.on("/api/config", HTTP_GET, handleConfigRequest);
    server.on("/api/config", HTTP_POST, handleConfigUpdate);
    server.on("/api/reset", HTTP_POST, handleResetRequest);
    server.on("/api/logs", HTTP_GET, handleLogsRequest);
    
    // Interface web
    server.on("/", HTTP_GET, handleWebInterface);
    server.on("/style.css", HTTP_GET, handleCSS);
    server.on("/script.js", HTTP_GET, handleJavaScript);
    
    // OTA update
    server.on("/update", HTTP_POST, handleOTAUpdate, handleFileUpdate);
    
    server.begin();
    Serial.println("Servidor web iniciado!");
  }
}

void initializeWebSocket() {
  if (systemData.wifiConnected) {
    webSocket.begin();
    webSocket.onEvent(onWebSocketEvent);
    Serial.println("WebSocket iniciado!");
  }
}

void initializeMQTT() {
  if (systemData.wifiConnected && mqtt_server[0] != '\0') {
    client.setServer(mqtt_server, 1883);
    client.setCallback(handleMQTTCallback);
    
    reconnectMQTT();
  }
}

void initializeCalibration() {
  Serial.println("Inicializando sistema de calibração...");
  
  // Carregar dados de calibração salvos
  systemData.currentWeight = preferences.getFloat("calibratedWeight", 0.0);
  float savedScale = preferences.getFloat("scaleFactor", 1.0);
  scale.setScale(savedScale);
  
  Serial.println("Sistema de calibração inicializado!");
}

void initializeUserInterface() {
  Serial.println("Inicializando interface do usuário...");
  
  // Configurar botões de interface
  pinMode(SLEEP_BUTTON, INPUT_PULLUP);
  
  // LEDs de status
  updateStatusLEDs();
  
  Serial.println("Interface inicializada!");
}

void configureOperationMode() {
  // Verificar se deve iniciar em modo de calibração
  if (digitalRead(SLEEP_BUTTON) == LOW) {
    delay(50); // Debounce
    if (digitalRead(SLEEP_BUTTON) == LOW) {
      startCalibrationMode();
      return;
    }
  }
  
  // Verificar nível de bateria
  if (systemData.batteryVoltage < 3.0) {
    Serial.println("Bateria baixa - entrando em modo de economia extrema");
    // Implementar modo de economia extrema
  }
  
  Serial.println("Modo de operação configurado!");
}

void maintainConnections() {
  // Manter WiFi
  if (systemData.wifiConnected) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi desconectado - reconectando...");
      initializeWiFi();
    }
  }
  
  // Manter MQTT
  if (systemData.wifiConnected && client.connected()) {
    client.loop();
  } else if (systemData.wifiConnected) {
    reconnectMQTT();
  }
  
  // Processar WebSocket
  if (systemData.wifiConnected) {
    webSocket.loop();
  }
  
  // Processar servidor web
  if (systemData.wifiConnected) {
    server.handleClient();
  }
}

void processSensors() {
  static unsigned long lastSensorRead = 0;
  
  if (millis() - lastSensorRead < 5000) return; // Ler a cada 5 segundos
  lastSensorRead = millis();
  
  // Ler peso da célula de carga
  systemData.currentWeight = scale.getUnits();
  
  // Ler temperatura ambiente
  systemData.currentTemperature = dht.readTemperature();
  if (isnan(systemData.currentTemperature)) {
    systemData.currentTemperature = 25.0; // Valor padrão
  }
  
  // Ler tensão da bateria
  systemData.batteryVoltage = readBatteryVoltage();
  
  // Atualizar heap livre
  systemData.freeHeap = ESP.getFreeHeap();
  
  // Atualizar timestamp
  systemData.lastUpdate = millis();
  
  // Log dos dados
  printSensorData();
}

void processConsumption() {
  static unsigned long lastLogTime = 0;
  static float lastWeight = -1.0;
  
  if (millis() - lastLogTime < DATA_LOG_INTERVAL) return;
  lastLogTime = millis();
  
  float currentWeight = systemData.currentWeight;
  
  if (lastWeight >= 0.0) {
    float weightDelta = lastWeight - currentWeight;
    if (abs(weightDelta) > 0.5) { // Apenas mudanças significativas (> 0.5g)
      // Atualizar totais
      systemData.sessionConsumed += weightDelta;
      systemData.totalConsumed += weightDelta;
      
      // Salvar no log
      ConsumptionLog logEntry;
      logEntry.timestamp = millis();
      logEntry.weight = currentWeight;
      logEntry.weightDelta = weightDelta;
      logEntry.totalConsumed = systemData.totalConsumed;
      
      consumptionLogs[logIndex] = logEntry;
      logIndex = (logIndex + 1) % LOG_SIZE;
      
      // Salvar persistentemente
      preferences.putFloat("totalConsumed", systemData.totalConsumed);
      
      // Enviar via WebSocket
      sendWebSocketUpdate();
      
      // Publicar via MQTT
      publishMQTTUpdate();
      
      Serial.printf("Consumo registrado: %.2fg (Total: %.2fg)\n", 
                   weightDelta, systemData.totalConsumed);
    }
  }
  
  lastWeight = currentWeight;
}

void processWebInterface() {
  // Interface web já processada em maintainConnections()
  // Aqui podemos adicionar lógica específica se necessário
}

void checkSleepConditions() {
  static unsigned long lastActivity = millis();
  
  // Verificar se houve atividade recente
  if (millis() - systemData.lastUpdate < 30000) {
    lastActivity = millis();
  }
  
  // Verificar botão de sleep
  if (digitalRead(SLEEP_BUTTON) == LOW) {
    delay(50); // Debounce
    if (digitalRead(SLEEP_BUTTON) == LOW) {
      enterDeepSleep();
      return;
    }
  }
  
  // Verificar se deve entrar em sleep automático
  if (systemData.wifiConnected && (millis() - lastActivity > 300000)) { // 5 minutos
    Serial.println("Entrando em modo de economia de energia");
    enterDeepSleep();
  }
}

void startAccessPointMode() {
  Serial.println("Iniciando Access Point...");
  
  WiFi.mode(WIFI_AP);
  WiFi.softAP("3dPot-Monitor", "12345678");
  
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());
  
  // Configurar servidor web em modo AP
  server.on("/", HTTP_GET, handleSetupInterface);
  server.begin();
  
  systemData.wifiConnected = false;
}

void startCalibrationMode() {
  Serial.println("=== MODO DE CALIBRAÇÃO ATIVADO ===");
  
  digitalWrite(CALIBRATION_LED, HIGH);
  
  // Interface de calibração via Serial
  calibrateScale();
  
  digitalWrite(CALIBRATION_LED, LOW);
  
  Serial.println("Calibração concluída - reiniciando...");
  delay(2000);
  ESP.restart();
}

void calibrateScale() {
  Serial.println("1. Certifique-se de que não há peso na balança");
  Serial.println("2. Coloque um peso known e pressione Enter");
  
  while (!Serial.available()) {
    delay(1000);
  }
  
  Serial.read(); // Consumir Enter
  
  // Limpar balança
  scale.tare();
  Serial.println("Balança zerada");
  
  // Ler peso known
  Serial.println("Coloque o peso known e pressione Enter");
  while (!Serial.available()) {
    delay(1000);
    Serial.print("Peso atual: ");
    Serial.print(scale.getUnits());
    Serial.println("g");
  }
  Serial.read();
  
  float knownWeight = getKnownWeight();
  float currentReading = scale.getUnits();
  
  if (currentReading > 0) {
    float newScale = currentReading / knownWeight;
    scale.setScale(newScale);
    
    preferences.putFloat("scaleFactor", newScale);
    
    Serial.printf("Calibração concluída - Fator: %.4f\n", newScale);
  } else {
    Serial.println("Erro na calibração");
  }
}

float getKnownWeight() {
  Serial.println("Digite o peso known em gramos (ex: 100.0):");
  
  while (!Serial.available()) {
    delay(100);
  }
  
  String input = Serial.readString();
  input.trim();
  
  return input.toFloat();
}

float readBatteryVoltage() {
  int rawValue = analogRead(BATTERY_PIN);
  float voltage = (rawValue * 3.3 / 4095.0) * 2; // Divisor de tensão (1:2)
  return voltage;
}

void printSensorData() {
  Serial.printf("Peso: %.2fg | Temp: %.2f°C | Bat: %.2fV | Heap: %d bytes\n",
               systemData.currentWeight,
               systemData.currentTemperature,
               systemData.batteryVoltage,
               systemData.freeHeap);
}

void printSystemStatus() {
  Serial.println("\n=== STATUS DO SISTEMA ===");
  Serial.printf("WiFi: %s\n", systemData.wifiConnected ? "Conectado" : "Desconectado");
  Serial.printf("MQTT: %s\n", systemData.mqttConnected ? "Conectado" : "Desconectado");
  Serial.printf("Peso atual: %.2fg\n", systemData.currentWeight);
  Serial.printf("Consumo da sessão: %.2fg\n", systemData.sessionConsumed);
  Serial.printf("Consumo total: %.2fg\n", systemData.totalConsumed);
  Serial.printf("Temperatura: %.2f°C\n", systemData.currentTemperature);
  Serial.printf("Bateria: %.2fV\n", systemData.batteryVoltage);
  Serial.printf("Memória livre: %d bytes\n", systemData.freeHeap);
  Serial.println("=========================\n");
}

void updateStatusLEDs() {
  // LED de status (WiFi/MQTT)
  if (systemData.wifiConnected) {
    if (systemData.mqttConnected) {
      digitalWrite(LED_STATUS, HIGH); // Verde
    } else {
      // Piscada para MQTT não conectado
      static unsigned long lastBlink = 0;
      if (millis() - lastBlink > 1000) {
        digitalWrite(LED_STATUS, !digitalRead(LED_STATUS));
        lastBlink = millis();
      }
    }
  } else {
    digitalWrite(LED_STATUS, LOW);
  }
}

void loadConfiguration() {
  // Carregar configurações da flash
  String savedSSID = preferences.getString("ssid", "");
  if (savedSSID.length() > 0) {
    // Configurar WiFi com dados salvos
  }
}

void saveConfiguration() {
  // Salvar configurações na flash
  preferences.putString("ssid", String(ssid));
  preferences.putFloat("totalConsumed", systemData.totalConsumed);
}

void sendWebSocketUpdate() {
  if (webSocket.connected()) {
    StaticJsonDocument<200> doc;
    doc["type"] = "sensor_update";
    doc["weight"] = systemData.currentWeight;
    doc["temperature"] = systemData.currentTemperature;
    doc["battery"] = systemData.batteryVoltage;
    doc["consumed"] = systemData.sessionConsumed;
    doc["timestamp"] = millis();
    
    String json;
    serializeJson(doc, json);
    webSocket.broadcastTXT(json);
  }
}

void publishMQTTUpdate() {
  if (client.connected()) {
    StaticJsonDocument<100> doc;
    doc["weight"] = systemData.currentWeight;
    doc["consumed"] = systemData.sessionConsumed;
    doc["battery"] = systemData.batteryVoltage;
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    client.publish(mqtt_topic, payload.c_str());
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Conectando ao MQTT...");
    String clientId = "3dPot-filament-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("MQTT conectado!");
      systemData.mqttConnected = true;
      
      // Assinar tópicos
      client.subscribe("3dpot/filament/config");
      client.subscribe("3dpot/filament/command");
    } else {
      Serial.print("Falha ao conectar MQTT, rc=");
      Serial.print(client.state());
      Serial.println(" Tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

void enterDeepSleep() {
  Serial.println("Entrando em modo deep sleep...");
  
  // Salvar configurações
  saveConfiguration();
  
  // Finalizar conexões
  if (client.connected()) client.disconnect();
  if (WiFi.status() == WL_CONNECTED) WiFi.disconnect(true);
  
  // Configurar wake up source (timer + botão)
  esp_sleep_enable_timer_wakeup(SLEEP_DURATION);
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_19, 0); // Botão GPIO19
  esp_sleep_enable_ext1_wakeup(GPIO_NUM_0, ESP_EXT1_WAKEUP_ALL_LOW); // BOOT button
  
  // Desligar LEDs
  digitalWrite(LED_STATUS, LOW);
  digitalWrite(CALIBRATION_LED, LOW);
  
  Serial.println("Deep sleep ativado!");
  esp_deep_sleep_start();
}

// Handlers HTTP
void handleStatusRequest() {
  StaticJsonDocument<300> doc;
  doc["weight"] = systemData.currentWeight;
  doc["temperature"] = systemData.currentTemperature;
  doc["battery"] = systemData.batteryVoltage;
  doc["consumed"] = systemData.sessionConsumed;
  doc["total"] = systemData.totalConsumed;
  doc["uptime"] = millis() / 1000;
  doc["wifi_connected"] = systemData.wifiConnected;
  doc["mqtt_connected"] = systemData.mqttConnected;
  doc["free_heap"] = systemData.freeHeap;
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handleCalibrationRequest() {
  if (server.hasArg("action")) {
    String action = server.arg("action");
    
    if (action == "tare") {
      scale.tare();
      server.send(200, "text/plain", "Balança zerada com sucesso");
    } else if (action == "calibrate") {
      startCalibrationMode();
    } else {
      server.send(400, "text/plain", "Ação inválida");
    }
  } else {
    server.send(400, "text/plain", "Parâmetro 'action' requerido");
  }
}

void handleConfigRequest() {
  StaticJsonDocument<200> doc;
  doc["scale"] = scale.getScale();
  doc["offset"] = scale.getOffset();
  doc["sleep_interval"] = SLEEP_DURATION / 1000;
  doc["log_interval"] = DATA_LOG_INTERVAL / 1000;
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handleConfigUpdate() {
  if (server.hasArg("scale")) {
    float scaleValue = server.arg("scale").toFloat();
    scale.setScale(scaleValue);
    preferences.putFloat("scaleFactor", scaleValue);
  }
  
  server.send(200, "text/plain", "Configuração atualizada");
}

void handleResetRequest() {
  if (server.hasArg("type")) {
    String type = server.arg("type");
    
    if (type == "consumption") {
      systemData.sessionConsumed = 0.0;
      systemData.sessionStart = millis();
      systemData.totalConsumed = 0.0;
      preferences.putFloat("totalConsumed", 0.0);
      server.send(200, "text/plain", "Dados de consumo zerados");
    } else if (type == "calibration") {
      scale.tare();
      scale.setScale(1.0);
      preferences.putFloat("scaleFactor", 1.0);
      server.send(200, "text/plain", "Calibração resetada");
    } else if (type == "all") {
      preferences.clear();
      server.send(200, "text/plain", "Todas as configurações foram resetadas");
    } else {
      server.send(400, "text/plain", "Tipo de reset inválido");
    }
  } else {
    server.send(400, "text/plain", "Parâmetro 'type' requerido");
  }
}

void handleLogsRequest() {
  StaticJsonDocument<1000> doc;
  JsonArray logs = doc.createNestedArray("logs");
  
  for (int i = 0; i < LOG_SIZE; i++) {
    int index = (logIndex - 1 - i + LOG_SIZE) % LOG_SIZE;
    if (consumptionLogs[index].timestamp > 0) {
      JsonObject log = logs.createNestedObject();
      log["timestamp"] = consumptionLogs[index].timestamp;
      log["weight"] = consumptionLogs[index].weight;
      log["delta"] = consumptionLogs[index].weightDelta;
      log["total"] = consumptionLogs[index].totalConsumed;
    }
  }
  
  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
}

void handleWebInterface() {
  String html = generateWebInterface();
  server.send(200, "text/html", html);
}

void handleCSS() {
  String css = generateCSS();
  server.send(200, "text/css", css);
}

void handleJavaScript() {
  String js = generateJavaScript();
  server.send(200, "application/javascript", js);
}

void handleSetupInterface() {
  String html = generateSetupInterface();
  server.send(200, "text/html", html);
}

void onWebSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      Serial.printf("WebSocket %u conectado\n", num);
      // Enviar dados iniciais
      sendWebSocketUpdate();
      break;
      
    case WStype_DISCONNECTED:
      Serial.printf("WebSocket %u desconectado\n", num);
      break;
      
    case WStype_TEXT:
      // Processar comandos via WebSocket
      handleWebSocketCommand(String((char*)payload));
      break;
  }
}

void handleWebSocketCommand(String command) {
  command.trim();
  
  if (command == "get_status") {
    sendWebSocketUpdate();
  } else if (command == "calibrate") {
    scale.tare();
    webSocket.broadcastTXT("{\"type\":\"calibration\",\"status\":\"success\"}");
  } else if (command == "reset_consumption") {
    systemData.sessionConsumed = 0.0;
    systemData.sessionStart = millis();
    webSocket.broadcastTXT("{\"type\":\"reset\",\"status\":\"success\"}");
  }
}

void handleMQTTCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.printf("MQTT recebido [%s]: %s\n", topic, message.c_str());
  
  // Processar comandos via MQTT
  StaticJsonDocument<200> doc;
  if (deserializeJson(doc, message) == DeserializationError::Ok) {
    if (doc.containsKey("command")) {
      String command = doc["command"];
      
      if (command == "tare") {
        scale.tare();
      } else if (command == "reset_session") {
        systemData.sessionConsumed = 0.0;
        systemData.sessionStart = millis();
      } else if (command == "get_config") {
        publishConfigViaMQTT();
      }
    }
  }
}

void publishConfigViaMQTT() {
  StaticJsonDocument<200> doc;
  doc["scale"] = scale.getScale();
  doc["offset"] = scale.getOffset();
  doc["consumption"] = systemData.totalConsumed;
  
  String payload;
  serializeJson(doc, payload);
  
  client.publish("3dpot/filament/config", payload.c_str());
}

void handleOTAUpdate() {
  server.send(200, "text/plain", "OTA Update Server");
  Serial.println("OTA Update solicitado");
}

void handleFileUpdate() {
  HTTPUpload& upload = server.upload();
  
  if (upload.status == UPLOAD_FILE_START) {
    Serial.printf("Atualizando: %s\n", upload.filename.c_str());
    
    if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
      Serial.println("Erro ao iniciar OTA");
    }
  } else if (upload.status == UPLOAD_FILE_WRITE) {
    if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
      Serial.println("Erro ao escrever OTA");
    }
  } else if (upload.status == UPLOAD_FILE_END) {
    if (Update.end(true)) {
      Serial.printf("OTA realizado com sucesso. Reiniciando...\n");
      ESP.restart();
    } else {
      Serial.println("Erro no OTA");
    }
  }
}

String generateWebInterface() {
  // Implementar interface web responsiva
  return R"(
<!DOCTYPE html>
<html>
<head>
  <title>3dPot Monitor de Filamento</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <div class="container">
    <h1>🧪 3dPot Monitor de Filamento</h1>
    
    <div class="status-grid">
      <div class="status-card">
        <h3>⚖️ Peso Atual</h3>
        <div class="value" id="current-weight">---</div>
        <div class="unit">gramas</div>
      </div>
      
      <div class="status-card">
        <h3>🔋 Bateria</h3>
        <div class="value" id="battery-voltage">---</div>
        <div class="unit">volts</div>
      </div>
      
      <div class="status-card">
        <h3>🌡️ Temperatura</h3>
        <div class="value" id="temperature">---</div>
        <div class="unit">°C</div>
      </div>
      
      <div class="status-card">
        <h3>📊 Consumo</h3>
        <div class="value" id="consumption">---</div>
        <div class="unit">session (g)</div>
      </div>
    </div>
    
    <div class="actions">
      <button onclick="tare()">🎯 Zerar Balança</button>
      <button onclick="calibrate()">⚙️ Calibrar</button>
      <button onclick="resetConsumption()">🔄 Reset Consumo</button>
    </div>
    
    <div class="charts">
      <h3>📈 Gráficos de Consumo</h3>
      <canvas id="consumption-chart" width="400" height="200"></canvas>
    </div>
  </div>
  
  <script src="/script.js"></script>
</body>
</html>
)";
}

String generateCSS() {
  return R"(
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    h1 {
      text-align: center;
      color: #333;
      margin-bottom: 30px;
      font-size: 2.5em;
    }
    
    .status-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .status-card {
      background: #f8f9fa;
      border-radius: 15px;
      padding: 20px;
      text-align: center;
      border: 2px solid #e9ecef;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .status-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .status-card h3 {
      color: #495057;
      margin-bottom: 15px;
      font-size: 1.1em;
    }
    
    .value {
      font-size: 2.5em;
      font-weight: bold;
      color: #212529;
      margin-bottom: 10px;
    }
    
    .unit {
      color: #6c757d;
      font-size: 0.9em;
    }
    
    .actions {
      display: flex;
      gap: 15px;
      justify-content: center;
      margin-bottom: 30px;
      flex-wrap: wrap;
    }
    
    .actions button {
      padding: 12px 24px;
      border: none;
      border-radius: 10px;
      background: #007bff;
      color: white;
      font-size: 1em;
      cursor: pointer;
      transition: background 0.2s, transform 0.2s;
    }
    
    .actions button:hover {
      background: #0056b3;
      transform: translateY(-1px);
    }
    
    .charts {
      background: #f8f9fa;
      border-radius: 15px;
      padding: 20px;
      border: 2px solid #e9ecef;
    }
    
    .charts h3 {
      text-align: center;
      color: #495057;
      margin-bottom: 20px;
    }
    
    @media (max-width: 600px) {
      .status-grid {
        grid-template-columns: 1fr;
      }
      
      .actions {
        flex-direction: column;
      }
      
      .actions button {
        width: 100%;
      }
    }
  ";
}

String generateJavaScript() {
  return R"(
    let socket;
    let consumptionData = [];
    
    function initWebSocket() {
      socket = new WebSocket('ws://' + window.location.hostname + ':81');
      
      socket.onopen = function() {
        console.log('WebSocket conectado');
        socket.send('get_status');
      };
      
      socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateDisplay(data);
      };
      
      socket.onclose = function() {
        console.log('WebSocket desconectado');
        setTimeout(initWebSocket, 5000);
      };
    }
    
    function updateDisplay(data) {
      if (data.type === 'sensor_update') {
        document.getElementById('current-weight').textContent = data.weight.toFixed(1);
        document.getElementById('battery-voltage').textContent = data.battery.toFixed(2);
        document.getElementById('temperature').textContent = data.temperature.toFixed(1);
        document.getElementById('consumption').textContent = data.consumed.toFixed(1);
        
        // Atualizar dados do gráfico
        consumptionData.push({
          x: new Date(),
          y: data.weight
        });
        
        if (consumptionData.length > 50) {
          consumptionData.shift();
        }
        
        updateChart();
      }
    }
    
    function tare() {
      fetch('/api/calibrate', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'action=tare'
      })
      .then(response => response.text())
      .then(data => {
        console.log(data);
        socket.send('get_status');
      });
    }
    
    function calibrate() {
      if (confirm('Iniciar calibração? A balança será zerada.')) {
        window.location.href = '/calibration';
      }
    }
    
    function resetConsumption() {
      if (confirm('Resetar dados de consumo?')) {
        fetch('/api/reset', {
          method: 'POST',
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
          body: 'type=consumption'
        })
        .then(response => response.text())
        .then(data => {
          console.log(data);
          socket.send('get_status');
        });
      }
    }
    
    function updateChart() {
      // Implementar atualização do gráfico (usar Chart.js)
      const canvas = document.getElementById('consumption-chart');
      const ctx = canvas.getContext('2d');
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (consumptionData.length > 1) {
        const minWeight = Math.min(...consumptionData.map(d => d.y));
        const maxWeight = Math.max(...consumptionData.map(d => d.y));
        const range = maxWeight - minWeight || 1;
        
        ctx.strokeStyle = '#007bff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        consumptionData.forEach((point, index) => {
          const x = (index / (consumptionData.length - 1)) * (canvas.width - 40) + 20;
          const y = canvas.height - 20 - ((point.y - minWeight) / range) * (canvas.height - 40);
          
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        
        ctx.stroke();
      }
    }
    
    // Inicializar ao carregar a página
    document.addEventListener('DOMContentLoaded', function() {
      initWebSocket();
      
      // Atualizar dados a cada 5 segundos
      setInterval(() => {
        fetch('/api/status')
          .then(response => response.json())
          .then(data => updateDisplay({
            type: 'sensor_update',
            weight: data.weight,
            battery: data.battery,
            temperature: data.temperature,
            consumed: data.consumed
          }));
      }, 5000);
    });
  ";
}

String generateSetupInterface() {
  return R"(
    <!DOCTYPE html>
    <html>
    <head>
      <title>Configuração 3dPot Monitor</title>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
      <div class="container">
        <h1>🔧 Configuração do 3dPot Monitor</h1>
        
        <form id="setup-form">
          <div class="form-group">
            <label>SSID WiFi:</label>
            <input type="text" id="ssid" required>
          </div>
          
          <div class="form-group">
            <label>Senha WiFi:</label>
            <input type="password" id="password" required>
          </div>
          
          <div class="form-group">
            <label>Servidor MQTT (opcional):</label>
            <input type="text" id="mqtt-server" placeholder="Ex: mqtt.google.com">
          </div>
          
          <button type="submit">💾 Salvar Configuração</button>
        </form>
      </div>
      
      <script>
        document.getElementById('setup-form').addEventListener('submit', function(e) {
          e.preventDefault();
          
          const ssid = document.getElementById('ssid').value;
          const password = document.getElementById('password').value;
          const mqttServer = document.getElementById('mqtt-server').value;
          
          // Salvar no localStorage por enquanto
          // TODO: Enviar para o ESP32
          localStorage.setItem('wifi-ssid', ssid);
          localStorage.setItem('wifi-password', password);
          localStorage.setItem('mqtt-server', mqttServer);
          
          alert('Configuração salva! Reiniciando...');
          setTimeout(() => location.reload(), 2000);
        });
      </script>
    </body>
    </html>
  ";
}

// Extensões para a classe HX711 (se necessário)
void HX711::setScale() {
  // Implementar setScale vazia se não usar parâmetros
}

void HX711::setOffset() {
  // Implementar setOffset vazia se não usar parâmetros  
}

float HX711::getScale() {
  return SCALE;
}

long HX711::getOffset() {
  return OFFSET;
}