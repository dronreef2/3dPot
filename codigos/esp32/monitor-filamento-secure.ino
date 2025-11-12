#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

// Include HX711 library
#include "HX711.h"

// Include configuration (only if it exists)
#ifdef CONFIG_H
#include "config.h"
#else
#include "config.example.h"
#endif

// ================================
// GLOBAL VARIABLES
// ================================
WebServer server(80);
HX711 scale;

// Configuration variables (will be set from config)
String wifi_ssid = WIFI_SSID;
String wifi_password = WIFI_PASSWORD;
String ap_ssid = AP_SSID;
String ap_password = AP_PASSWORD;

bool mqtt_enabled = MQTT_ENABLE;
String mqtt_server = MQTT_SERVER;
int mqtt_port = MQTT_PORT;
String mqtt_user = MQTT_USER;
String mqtt_password = MQTT_PASSWORD;
String mqtt_topic_prefix = MQTT_TOPIC_PREFIX;

// Weight calibration variables
float carretel_vazio_peso_g = CARRETEL_VAZIO_PESO_G;
float filamento_maximo_g = FILAMENTO_MAXIMO_G;
float alerta_critico_percent = ALERTA_CRITICO_PERCENT;
float alerta_baixo_percent = ALERTA_BAIXO_PERCENT;

// State tracking
bool wifi_connected = false;
unsigned long last_weight_read = 0;
unsigned long last_mqtt_send = 0;
unsigned long wifi_reconnect_attempts = 0;

void setup() {
#if DEBUG_SERIAL
  Serial.begin(DEBUG_SERIAL_BAUDRATE);
  Serial.println("\n=== 3dPot ESP32 Monitor Starting ===");
#endif

  // Initialize pins
  pinMode(LED_STATUS_PIN, OUTPUT);
  pinMode(LED_WIFI_PIN, OUTPUT);
  pinMode(BUTTON_CALIBRATE_PIN, INPUT_PULLUP);
  
  // Initialize weight sensor
  initializeWeightSensor();
  
  // Initialize WiFi
  initializeWiFi();
  
  // Initialize OTA (if enabled)
  if (OTA_ENABLE) {
    initializeOTA();
  }
  
  // Setup web server routes
  setupWebServer();
  
  // Initialize MQTT (if enabled)
  if (mqtt_enabled) {
    initializeMQTT();
  }
  
#if DEBUG_SERIAL
  Serial.println("=== Setup Complete ===");
  Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
#endif
}

void loop() {
  // Handle OTA updates
  if (OTA_ENABLE) {
    ArduinoOTA.handle();
  }
  
  // Handle web server
  server.handleClient();
  
  // Check WiFi connection and reconnect if needed
  checkWiFiConnection();
  
  // Read weight sensor every 5 seconds
  unsigned long current_time = millis();
  if (current_time - last_weight_read >= API_UPDATE_INTERVAL_MS) {
    updateWeightData();
    last_weight_read = current_time;
  }
  
  // Send MQTT data every 10 seconds
  if (mqtt_enabled && current_time - last_mqtt_send >= 10000) {
    sendMQTTData();
    last_mqtt_send = current_time;
  }
  
  // Handle button press for calibration
  handleButtonPress();
  
  // Update status LED
  updateStatusLED();
  
  delay(100); // Small delay to prevent watchdog reset
}

// ================================
// INITIALIZATION FUNCTIONS
// ================================

void initializeWeightSensor() {
#if DEBUG_SERIAL
  Serial.println("Initializing weight sensor...");
#endif

  scale.begin(HX711_DOUT_PIN, HX711_SCK_PIN);
  
  // Set gain and offset
  scale.set_gain(HX711_GAIN);
  scale.set_scale(HX711_SCALE_FACTOR);
  
  // Tare (zero) the scale
  scale.tare();
  
  if (scale.is_ready()) {
#if DEBUG_SERIAL
    Serial.println("Weight sensor ready");
#endif
    // Blink LED to indicate success
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_STATUS_PIN, HIGH);
      delay(200);
      digitalWrite(LED_STATUS_PIN, LOW);
      delay(200);
    }
  } else {
#if DEBUG_SERIAL
    Serial.println("ERROR: Weight sensor not ready!");
#endif
    // Fast blink LED to indicate error
    while (true) {
      digitalWrite(LED_STATUS_PIN, HIGH);
      delay(100);
      digitalWrite(LED_STATUS_PIN, LOW);
      delay(100);
    }
  }
}

void initializeWiFi() {
#if DEBUG_SERIAL
  Serial.println("Connecting to WiFi...");
#endif
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifi_ssid.c_str(), wifi_password.c_str());
  
  unsigned long start_time = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start_time > WIFI_TIMEOUT_MS) {
      break; // Timeout reached
    }
    
#if DEBUG_SERIAL
    Serial.print(".");
#endif
    delay(500);
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifi_connected = true;
    wifi_reconnect_attempts = 0;
    
#if DEBUG_SERIAL
    Serial.println("\nWiFi Connected!");
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());
#endif
    
    digitalWrite(LED_WIFI_PIN, HIGH);
    
  } else {
#if DEBUG_SERIAL
    Serial.println("\nFailed to connect to WiFi, starting Access Point...");
#endif
    
    // Start Access Point
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ap_ssid.c_str(), ap_password.c_str(), AP_CHANNEL);
    
    IPAddress IP = WiFi.softAPIP();
#if DEBUG_SERIAL
    Serial.printf("Access Point started: %s\n", IP.toString().c_str());
#endif
    
    wifi_connected = false;
  }
}

void initializeOTA() {
#if DEBUG_SERIAL
  Serial.println("Initializing OTA updates...");
#endif

  ArduinoOTA.setHostname(OTA_HOSTNAME);
  ArduinoOTA.setPassword(OTA_PASSWORD);
  
  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_SPIFFS
      type = "filesystem";
    }
    
#if DEBUG_SERIAL
    Serial.println("OTA Update Starting: " + type);
#endif
    digitalWrite(LED_STATUS_PIN, HIGH); // Turn on LED during update
  });
  
  ArduinoOTA.onEnd([]() {
#if DEBUG_SERIAL
    Serial.println("\nOTA Update Complete");
#endif
    digitalWrite(LED_STATUS_PIN, LOW);
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
#if DEBUG_SERIAL
    Serial.printf("OTA Progress: %u%%\r", (progress / (total / 100)));
#endif
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
#if DEBUG_SERIAL
    Serial.printf("OTA Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
#endif
  });
  
  ArduinoOTA.begin();
#if DEBUG_SERIAL
  Serial.println("OTA ready");
#endif
}

void setupWebServer() {
  // Main dashboard
  server.on("/", HTTP_GET, handleRoot);
  
  // API endpoints
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/calibrate", HTTP_POST, handleCalibrate);
  server.on("/api/config", HTTP_POST, handleConfig);
  server.on("/api/reset", HTTP_POST, handleReset);
  
  // Configuration endpoints
  server.on("/config", HTTP_GET, handleConfigPage);
  server.on("/config", HTTP_POST, handleConfigSave);
  
  // Health check
  server.on("/health", HTTP_GET, handleHealth);
  
#if DEBUG_SERIAL
  Serial.printf("Web server started on port %d\n", HTTP_SERVER_PORT);
#endif
  
  server.begin();
}

void initializeMQTT() {
  // MQTT initialization would go here
  // Note: This requires additional MQTT library include
#if DEBUG_SERIAL
  Serial.println("MQTT not implemented in this version");
#endif
}

// ================================
// WEB SERVER HANDLERS
// ================================

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>3dPot Monitor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="10">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container { 
            max-width: 500px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        h1 { text-align: center; margin-bottom: 30px; }
        .data { 
            margin: 20px 0; 
            font-size: 18px; 
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        .progress { 
            width: 100%; 
            height: 30px; 
            background: rgba(255,255,255,0.3); 
            border-radius: 15px; 
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-bar { 
            height: 100%; 
            border-radius: 15px; 
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .status-normal { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
        .status-low { background: linear-gradient(90deg, #FF9800, #FFC107); }
        .status-critical { background: linear-gradient(90deg, #F44336, #FF5722); }
        .button { 
            padding: 15px 30px; 
            font-size: 16px; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 10px;
            background: rgba(255,255,255,0.2);
            color: white;
            transition: all 0.3s;
        }
        .button:hover { background: rgba(255,255,255,0.3); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 3dPot Monitor</h1>
        
        <div class="data">
            <div class="grid">
                <div><strong>📊 Peso Atual:</strong></div>
                <div><span id="pesoAtual">---</span> g</div>
                
                <div><strong>🧵 Filamento:</strong></div>
                <div><span id="filamentoRestante">---</span>%</div>
                
                <div><strong>⚡ Status:</strong></div>
                <div><span id="status">Carregando...</span></div>
                
                <div><strong>📶 WiFi:</strong></div>
                <div><span id="wifiStatus">Verificando...</span></div>
                
                <div><strong>💾 Memória:</strong></div>
                <div><span id="memory">---</span></div>
            </div>
        </div>
        
        <div class="progress">
            <div class="progress-bar status-normal" id="progressBar" style="width: 0%">
                <span id="progressText">0%</span>
            </div>
        </div>
        
        <div class="data">
            <button class="button" onclick="calibrate()">🔄 Calibrar</button>
            <button class="button" onclick="reset()">⚡ Reset</button>
            <button class="button" onclick="config()">⚙️ Config</button>
        </div>
    </div>
    
    <script>
        let updateInterval;
        
        function updateData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('pesoAtual').textContent = data.peso_atual.toFixed(1);
                    document.getElementById('filamentoRestante').textContent = data.percentagem_restante.toFixed(1);
                    document.getElementById('status').textContent = data.status;
                    document.getElementById('wifiStatus').textContent = data.wifi_connected ? '🟢 Conectado' : '🟡 AP Mode';
                    document.getElementById('memory').textContent = data.free_heap + ' bytes';
                    
                    // Update progress bar
                    const percent = data.percentagem_restante;
                    const progressBar = document.getElementById('progressBar');
                    const progressText = document.getElementById('progressText');
                    
                    progressBar.style.width = percent + '%';
                    progressText.textContent = percent.toFixed(1) + '%';
                    
                    // Set color class
                    progressBar.className = 'progress-bar';
                    if (percent < 10) {
                        progressBar.classList.add('status-critical');
                    } else if (percent < 25) {
                        progressBar.classList.add('status-low');
                    } else {
                        progressBar.classList.add('status-normal');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    document.getElementById('status').textContent = 'Erro de conexão';
                });
        }
        
        function calibrate() {
            if (confirm('Calibrar carretel vazio?\n\nCertifique-se de que o carretel vazio está na balança.')) {
                fetch('/api/calibrate', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.sucesso) {
                            alert('✅ Calibração realizada com sucesso!\nPeso vazio: ' + data.peso_vazio.toFixed(1) + 'g');
                            updateData();
                        } else {
                            alert('❌ Erro na calibração: ' + data.erro);
                        }
                    })
                    .catch(error => alert('❌ Erro de conexão'));
            }
        }
        
        function reset() {
            if (confirm('Resetar balança?')) {
                fetch('/api/reset', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert('✅ Balança resetada!');
                        updateData();
                    });
            }
        }
        
        function config() {
            window.location.href = '/config';
        }
        
        // Update data every 10 seconds
        updateData();
        updateInterval = setInterval(updateData, 10000);
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            clearInterval(updateInterval);
        });
    </script>
</body>
</html>
  )";
  
  server.send(200, "text/html", html);
}

void handleStatus() {
  DynamicJsonDocument doc(1024);
  
  // Read weight data
  float peso_atual = scale.get_units(3);
  float peso_filamento = peso_atual - carretel_vazio_peso_g;
  float percentagem_restante = 0;
  
  if (peso_filamento > 0) {
    percentagem_restante = (peso_filamento / filamento_maximo_g) * 100;
    percentagem_restante = constrain(percentagem_restante, 0, 100);
  }
  
  // Determine status
  String status = "NORMAL";
  if (percentagem_restante < alerta_critico_percent) {
    status = "CRÍTICO";
  } else if (percentagem_restante < alerta_baixo_percent) {
    status = "BAIXO";
  }
  
  // Fill JSON response
  doc["peso_atual"] = peso_atual;
  doc["peso_filamento"] = peso_filamento;
  doc["peso_carretel_vazio"] = carretel_vazio_peso_g;
  doc["peso_maximo_filamento"] = filamento_maximo_g;
  doc["percentagem_restante"] = percentagem_restante;
  doc["status"] = status;
  doc["alertas"] = getAlerts();
  doc["wifi_connected"] = wifi_connected;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["uptime"] = millis() / 1000;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["timestamp"] = millis();
  
  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleCalibrate() {
  if (scale.is_ready()) {
    float calibracao_samples[CALIBRATION_SAMPLES];
    float soma = 0;
    
    // Take multiple samples for accuracy
    for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
      calibracao_samples[i] = scale.get_units(1);
      soma += calibracao_samples[i];
      delay(100);
    }
    
    float peso_vazio = soma / CALIBRATION_SAMPLES;
    carretel_vazio_peso_g = peso_vazio;
    
#if DEBUG_SERIAL
    Serial.printf("Calibration complete. Empty weight: %.1fg\n", peso_vazio);
#endif
    
    DynamicJsonDocument doc(512);
    doc["sucesso"] = true;
    doc["peso_vazio"] = peso_vazio;
    doc["amostras"] = CALIBRATION_SAMPLES;
    doc["desvio_padrao"] = calculateStandardDeviation(calibracao_samples, CALIBRATION_SAMPLES);
    
    String json;
    serializeJson(doc, json);
    server.send(200, "application/json", json);
  } else {
    server.send(400, "application/json", "{\"sucesso\": false, \"erro\": \"Sensor não pronto\"}");
  }
}

void handleConfig() {
  DynamicJsonDocument doc(512);
  doc["carretel_vazio_peso_g"] = carretel_vazio_peso_g;
  doc["filamento_maximo_g"] = filamento_maximo_g;
  doc["alerta_critico_percent"] = alerta_critico_percent;
  doc["alerta_baixo_percent"] = alerta_baixo_percent;
  doc["mqtt_enabled"] = mqtt_enabled;
  
  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleReset() {
  scale.tare();
  
#if DEBUG_SERIAL
  Serial.println("Scale reset (tare)");
#endif
  
  DynamicJsonDocument doc(256);
  doc["sucesso"] = true;
  doc["mensagem"] = "Balança resetada com sucesso";
  
  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleConfigPage() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>3dPot Config</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; margin: 20px; }
        .form-group { margin: 15px 0; }
        label { display: inline-block; width: 200px; font-weight: bold; }
        input { padding: 8px; width: 150px; }
        button { padding: 10px 20px; margin: 10px 5px; }
    </style>
</head>
<body>
    <h1>⚙️ Configurações</h1>
    <form id="configForm">
        <div class="form-group">
            <label>Peso Carretel Vazio (g):</label>
            <input type="number" id="carretelVazio" step="0.1">
        </div>
        <div class="form-group">
            <label>Filamento Máximo (g):</label>
            <input type="number" id="filamentoMaximo" step="0.1">
        </div>
        <div class="form-group">
            <label>Alerta Crítico (%):</label>
            <input type="number" id="alertaCritico" step="0.1">
        </div>
        <div class="form-group">
            <label>Alerta Baixo (%):</label>
            <input type="number" id="alertaBaixo" step="0.1">
        </div>
        <button type="submit">Salvar</button>
        <button type="button" onclick="window.location.href='/'">Voltar</button>
    </form>
    
    <script>
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                document.getElementById('carretelVazio').value = data.carretel_vazio_peso_g;
                document.getElementById('filamentoMaximo').value = data.filamento_maximo_g;
                document.getElementById('alertaCritico').value = data.alerta_critico_percent;
                document.getElementById('alertaBaixo').value = data.alerta_baixo_percent;
            });
            
        document.getElementById('configForm').onsubmit = function(e) {
            e.preventDefault();
            
            const config = {
                carretel_vazio_peso_g: parseFloat(document.getElementById('carretelVazio').value),
                filamento_maximo_g: parseFloat(document.getElementById('filamentoMaximo').value),
                alerta_critico_percent: parseFloat(document.getElementById('alertaCritico').value),
                alerta_baixo_percent: parseFloat(document.getElementById('alertaBaixo').value)
            };
            
            fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    alert('✅ Configurações salvas!');
                    window.location.href = '/';
                } else {
                    alert('❌ Erro ao salvar: ' + data.erro);
                }
            });
        };
    </script>
</body>
</html>
  )";
  
  server.send(200, "text/html", html);
}

void handleConfigSave() {
  // Handle POST config save
  String message = "Configuração salva";
  server.send(200, "text/plain", message);
}

void handleHealth() {
  DynamicJsonDocument doc(256);
  doc["status"] = "ok";
  doc["uptime"] = millis();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["weight_sensor_ready"] = scale.is_ready();
  doc["wifi_connected"] = wifi_connected;
  
  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

// ================================
// HELPER FUNCTIONS
// ================================

void checkWiFiConnection() {
  static unsigned long last_check = 0;
  static bool was_connected = false;
  
  if (millis() - last_check > 30000) { // Check every 30 seconds
    last_check = millis();
    
    bool current_status = (WiFi.status() == WL_CONNECTED);
    
    if (current_status != was_connected) {
      if (current_status) {
        wifi_connected = true;
        wifi_reconnect_attempts = 0;
        digitalWrite(LED_WIFI_PIN, HIGH);
#if DEBUG_SERIAL
        Serial.println("WiFi reconnected");
#endif
      } else {
        wifi_connected = false;
        digitalWrite(LED_WIFI_PIN, LOW);
#if DEBUG_SERIAL
        Serial.println("WiFi disconnected");
#endif
      }
      was_connected = current_status;
    }
  }
}

void updateWeightData() {
  if (!scale.is_ready()) {
#if DEBUG_SERIAL
    Serial.println("Weight sensor not ready");
#endif
    return;
  }
  
  // Weight data is read in handleStatus() when requested
  // This function can be used for logging or additional processing
}

void sendMQTTData() {
  // MQTT implementation would go here
  // This would require additional MQTT library and setup
}

void handleButtonPress() {
  static unsigned long last_button_check = 0;
  static bool button_was_pressed = false;
  
  if (millis() - last_button_check > 100) { // Debounce button
    last_button_check = millis();
    
    bool button_pressed = (digitalRead(BUTTON_CALIBRATE_PIN) == LOW);
    
    if (button_pressed && !button_was_pressed) {
      // Button just pressed - trigger calibration
#if DEBUG_SERIAL
      Serial.println("Calibration button pressed");
#endif
      // Optional: auto-calibrate or show indication
      digitalWrite(LED_STATUS_PIN, HIGH);
    } else if (!button_pressed && button_was_pressed) {
      // Button released
      digitalWrite(LED_STATUS_PIN, LOW);
    }
    
    button_was_pressed = button_pressed;
  }
}

void updateStatusLED() {
  static unsigned long last_led_update = 0;
  
  if (millis() - last_led_update > 500) { // Update LED every 500ms
    last_led_update = millis();
    
    // Read current weight for status determination
    if (scale.is_ready()) {
      float peso_atual = scale.get_units(1);
      float peso_filamento = peso_atual - carretel_vazio_peso_g;
      float percentagem_restante = (peso_filamento / filamento_maximo_g) * 100;
      
      if (percentagem_restante < alerta_critico_percent) {
        // Fast blink - critical
        digitalWrite(LED_STATUS_PIN, (millis() % 400) < 200);
      } else if (percentagem_restante < alerta_baixo_percent) {
        // Slow blink - low
        digitalWrite(LED_STATUS_PIN, (millis() % 1000) < 100);
      } else {
        // Solid on - normal
        digitalWrite(LED_STATUS_PIN, HIGH);
      }
    }
  }
}

float calculateStandardDeviation(float* values, int count) {
  float mean = 0;
  for (int i = 0; i < count; i++) {
    mean += values[i];
  }
  mean /= count;
  
  float variance = 0;
  for (int i = 0; i < count; i++) {
    variance += (values[i] - mean) * (values[i] - mean);
  }
  variance /= count;
  
  return sqrt(variance);
}

String getAlerts() {
  if (!scale.is_ready()) {
    return "Sensor não pronto";
  }
  
  float peso_atual = scale.get_units(1);
  float peso_filamento = peso_atual - carretel_vazio_peso_g;
  float percentagem_restante = (peso_filamento / filamento_maximo_g) * 100;
  
  if (percentagem_restante < alerta_critico_percent) {
    return "Filamento crítico! Substitua em breve.";
  } else if (percentagem_restante < alerta_baixo_percent) {
    return "Filamento baixo. Prepare reposição.";
  } else {
    return "Níveis normais.";
  }
}