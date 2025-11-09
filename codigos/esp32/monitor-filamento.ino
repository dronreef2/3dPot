#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "HX711.h"

// Configuração WiFi
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";

// Pinos
const int HX711_DOUT = 4;
const int HX711_SCK = 5;
const int LED_STATUS = 2;

// Objetos
WebServer server(80);
HX711 scale;

// Variáveis de calibração
float pesoCarretelVazio = 200.0;  // Ajuste conforme seu carretel
float pesoMaximoFilamento = 1000.0;  // Capacidade máxima do carretel

void setup() {
  Serial.begin(115200);
  
  // Inicializa sensor de peso
  scale.begin(HX711_DOUT, HX711_SCK);
  scale.set_scale(2280.0);  // Fator de escala (calibre sua balança)
  scale.tare();  // Zera a balança
  
  // Conecta WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("WiFi conectado!");
  Serial.println(WiFi.localIP());

  // Configura rotas web
  server.on("/", handleRoot);
  server.on("/api/status", handleStatus);
  server.on("/api/calibrate", HTTP_POST, handleCalibrate);
  
  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  server.handleClient();
  
  // Atualiza a cada 5 segundos
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 5000) {
    updateSensorData();
    lastUpdate = millis();
  }
}

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Monitor de Filamento</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial; text-align: center; margin: 50px; }
        .container { max-width: 400px; margin: 0 auto; }
        .progress { width: 100%; height: 30px; background: #ddd; border-radius: 15px; }
        .progress-bar { height: 100%; background: #4CAF50; border-radius: 15px; transition: width 0.3s; }
        .data { margin: 20px 0; font-size: 18px; }
        .calibrate-btn { padding: 10px 20px; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Monitor de Filamento</h1>
        <div class="data">
            <div>Peso Atual: <span id="pesoAtual">---</span> g</div>
            <div>Filamento Restante: <span id="filamentoRestante">---</span>%</div>
            <div>Status: <span id="status">Carregando...</span></div>
        </div>
        <div class="progress">
            <div class="progress-bar" id="progressBar" style="width: 0%"></div>
        </div>
        <button class="calibrate-btn" onclick="calibrate()">Calibrar Carretel Vazio</button>
    </div>
    
    <script>
        function updateData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('pesoAtual').textContent = data.peso_atual.toFixed(1);
                    document.getElementById('filamentoRestante').textContent = data.percentagem_restante.toFixed(1);
                    document.getElementById('status').textContent = data.status;
                    document.getElementById('progressBar').style.width = data.percentagem_restante + '%';
                })
                .catch(error => console.error('Erro:', error));
        }
        
        function calibrate() {
            fetch('/api/calibrate', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Calibração realizada: ' + data.peso_vazio.toFixed(1) + 'g');
                    updateData();
                });
        }
        
        setInterval(updateData, 5000);
        updateData();
    </script>
</body>
</html>
  )";
  
  server.send(200, "text/html", html);
}

void handleStatus() {
  float pesoAtual = scale.get_units(3);
  float pesoFilamento = pesoAtual - pesoCarretelVazio;
  float porcentagemRestante = 0;
  
  if (pesoFilamento > 0) {
    porcentagemRestante = (pesoFilamento / pesoMaximoFilamento) * 100;
    porcentagemRestante = constrain(porcentagemRestante, 0, 100);
  }
  
  String status = "OK";
  if (porcentagemRestante < 10) {
    status = "CRÍTICO";
  } else if (porcentagemRestante < 25) {
    status = "BAIXO";
  }
  
  DynamicJsonDocument doc(1024);
  doc["peso_atual"] = pesoAtual;
  doc["peso_filamento"] = pesoFilamento;
  doc["peso_carretel_vazio"] = pesoCarretelVazio;
  doc["percentagem_restante"] = porcentagemRestante;
  doc["status"] = status;
  doc["timestamp"] = millis();
  
  String json;
  serializeJson(doc, json);
  server.send(200, "application/json", json);
}

void handleCalibrate() {
  if (scale.is_ready()) {
    pesoCarretelVazio = scale.get_units(10);
    DynamicJsonDocument doc(512);
    doc["sucesso"] = true;
    doc["peso_vazio"] = pesoCarretelVazio;
    
    String json;
    serializeJson(doc, json);
    server.send(200, "application/json", json);
  } else {
    server.send(400, "application/json", "{\"sucesso\": false, \"erro\": \"Sensor não pronto\"}");
  }
}

void updateSensorData() {
  // Atualiza LED de status baseado na quantidade de filamento
  float pesoAtual = scale.get_units(1);
  float pesoFilamento = pesoAtual - pesoCarretelVazio;
  float porcentagemRestante = (pesoFilamento / pesoMaximoFilamento) * 100;
  
  if (porcentagemRestante < 10) {
    // Piscada rápida - crítico
    digitalWrite(LED_STATUS, millis() % 200 < 100);
  } else if (porcentagemRestante < 25) {
    // Piscada lenta - baixo
    digitalWrite(LED_STATUS, millis() % 1000 < 100);
  } else {
    // LED aceso - normal
    digitalWrite(LED_STATUS, HIGH);
  }
  
  // Log no serial
  Serial.printf("Peso: %.1fg | Filamento: %.1fg | Restante: %.1f%% | Status: %s\n", 
                pesoAtual, pesoFilamento, porcentagemRestante, 
                (porcentagemRestante < 10 ? "CRÍTICO" : porcentagemRestante < 25 ? "BAIXO" : "NORMAL"));
}
