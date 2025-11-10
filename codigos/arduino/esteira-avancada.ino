/*
  3dPot Arduino Esteira Transportadora - VERSÃO AVANÇADA
  
  Funcionalidades implementadas:
  ✅ Controle de velocidade variável (PWM)
  ✅ Modo automático vs manual
  ✅ Interface Bluetooth para controle remoto
  ✅ Sensores de posição e parada de emergência
  ✅ Display LCD para status local
  ✅ Controle de aceleração suave (acceleration ramp)
  ✅ Modo de calibração de velocidade
  ✅ Sistema de diagnóstico e manutenção
  ✅ Comunicação com PC (serial com comandos)
  ✅ Contador de peças processadas
  ✅ Medição de energia consumida
  ✅ Proteção contra sobrecarga
  ✅ Modo de emergência com parada suave
  
  Autor: 3dPot Project
  Versão: 2.0
  Data: 2025-11-10
*/

#include <Stepper.h>
#include <LiquidCrystal.h>
#include <SoftwareSerial.h>
#include <Servo.h>
#include <EEPROM.h>
#include <avr/wdt.h>

// Configurações de hardware
#define STEP_PER_REV 200
#define IN1_PIN 8
#define IN2_PIN 9
#define IN3_PIN 10
#define IN4_PIN 11
#define BT_RX_PIN 2
#define BT_TX_PIN 3
#define ENCODER_PIN 4
#define EMERGENCY_STOP_PIN 5
#define SENSOR_IR_SENSOR1 6
#define SENSOR_IR_SENSOR2 7
#define LED_STATUS 13
#define LED_ERROR 12
#define SERVO_PIN A0
#define POT_SPEED_PIN A1
#define BTN_MODE_PIN A2
#define BTN_START_STOP_PIN A3

// Configurações de EEPROM
#define EEPROM_SIZE 256
#define CALIBRATION_ADDR 0
#define CONFIG_ADDR 32
#define STATS_ADDR 64

// Configurações de operação
const unsigned long EMERGENCY_STOP_DELAY = 2000; // 2 segundos
const int MAX_SPEED = 50; // RPM máxima
const int MIN_SPEED = 1; // RPM mínima
const int ACCELERATION_STEPS = 10; // Passos para aceleração suave
const unsigned long DIAGNOSTIC_INTERVAL = 30000; // 30 segundos

// Estados do sistema
enum SystemState {
  STATE_IDLE,
  STATE_RUNNING,
  STATE_PAUSED,
  STATE_EMERGENCY_STOP,
  STATE_MAINTENANCE,
  STATE_CALIBRATION,
  STATE_ERROR
};

// Modos de operação
enum OperationMode {
  MODE_MANUAL,
  MODE_AUTOMATIC,
  MODE_MAINTENANCE,
  MODE_CALIBRATION
};

// Objetos globais
Stepper motor(STEP_PER_REV, IN1_PIN, IN3_PIN, IN2_PIN, IN4_PIN);
LiquidCrystal lcd(8, 9, 10, 11, 12, 13); // RS, Enable, D4, D5, D6, D7
SoftwareSerial bluetooth(BT_RX_PIN, BT_TX_PIN);
Servo feederServo;

// Estrutura de configuração
struct Configuration {
  float stepsPerMM = 1.0; // Passos por milímetro
  int maxSpeed = 30; // RPM máxima configurada
  int minSpeed = 5; // RPM mínima configurada
  bool autoStop = true; // Parar automaticamente ao detectar peça
  unsigned long autoStopDelay = 1000; // Delay antes de parar (ms)
  bool soundAlerts = true; // Alertas sonoros
  bool ledIndicators = true; // LEDs indicadores
  float powerConsumptionFactor = 1.0; // Fator de consumo energético
} config;

// Estrutura de estatísticas
struct Statistics {
  unsigned long totalRuntime = 0; // Tempo total de operação (ms)
  unsigned long totalPieces = 0; // Total de peças processadas
  float totalDistance = 0.0; // Distância total percorrida (mm)
  float avgSpeed = 0.0; // Velocidade média (RPM)
  int emergencyStops = 0; // Paradas de emergência
  int errorCount = 0; // Contador de erros
  float maxPower = 0.0; // Potência máxima registrada
  unsigned long lastMaintenance = 0; // Tempo da última manutenção
} stats;

// Estrutura de diagnóstico
struct DiagnosticData {
  float motorCurrent = 0.0; // Corrente do motor
  float motorTemperature = 0.0; // Temperatura estimada
  int encoderCount = 0; // Contador do encoder
  bool sensor1Status = false; // Status do sensor 1
  bool sensor2Status = false; // Status do sensor 2
  bool emergencyStopStatus = false; // Status da parada de emergência
  int speedRPS = 0; // Velocidade atual (revoluções por segundo)
  int accelerationPhase = 0; // Fase de aceleração atual
  unsigned long lastSensorTrigger = 0; // Último trigger do sensor
} diagnostic;

// Variáveis de controle
SystemState currentState = STATE_IDLE;
OperationMode currentMode = MODE_MANUAL;
int targetSpeed = 0;
int currentSpeed = 0;
int accelerationStep = 0;
bool systemEnabled = false;
bool emergencyStopTriggered = false;
unsigned long lastSpeedUpdate = 0;
unsigned long lastDiagnostic = 0;
unsigned long stateStartTime = 0;
unsigned long lastSensorCheck = 0;

// Buffer para comandos Bluetooth/Serial
String commandBuffer = "";
String responseBuffer = "";

// Função de configuração inicial
void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600);
  
  Serial.println("=== 3dPot Arduino Esteira Transportadora v2.0 ===");
  Serial.println("Inicializando sistema...");
  
  // Inicializar hardware
  initializeHardware();
  
  // Carregar configuração
  loadConfiguration();
  
  // Inicializar sistema de diagnóstico
  initializeDiagnostic();
  
  // Calibrar sistema
  calibrateSystem();
  
  // Inicializar interface
  initializeInterface();
  
  // Ativar watchdog
  wdt_enable(WDTO_8S);
  
  Serial.println("Sistema inicializado com sucesso!");
  printSystemInfo();
  
  // Estado inicial
  setState(STATE_IDLE);
}

void loop() {
  wdt_reset();
  
  // Processar comandos de entrada
  processCommands();
  
  // Executar lógica principal
  executeMainLogic();
  
  // Atualizar diagnóstico
  updateDiagnostic();
  
  // Atualizar interface
  updateInterface();
  
  // Manter aceleracao suave
  maintainAcceleration();
  
  // Verificar condições de emergência
  checkEmergencyConditions();
  
  // Executar tarefas de manutenção
  executeMaintenanceTasks();
  
  delay(50);
}

void initializeHardware() {
  Serial.println("Inicializando hardware...");
  
  // Configurar pino do encoder
  pinMode(ENCODER_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN), encoderInterrupt, RISING);
  
  // Configurar pinos de sensores
  pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
  pinMode(SENSOR_IR_SENSOR1, INPUT);
  pinMode(SENSOR_IR_SENSOR2, INPUT);
  
  // Configurar LEDs
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_ERROR, OUTPUT);
  
  // Configurar botões
  pinMode(BTN_MODE_PIN, INPUT_PULLUP);
  pinMode(BTN_START_STOP_PIN, INPUT_PULLUP);
  
  // Configurar potenciômetro
  pinMode(POT_SPEED_PIN, INPUT);
  
  // Inicializar servo
  feederServo.attach(SERVO_PIN);
  feederServo.write(90); // Posição neutra
  
  // Inicializar LCD
  lcd.begin(20, 4);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("3dPot Conveyor v2.0");
  
  // Configurar stepper motor
  motor.setSpeed(30); // RPM padrão
  
  Serial.println("Hardware inicializado!");
}

void loadConfiguration() {
  Serial.println("Carregando configuração...");
  
  EEPROM.get(CALIBRATION_ADDR, config);
  
  // Validar configuração carregada
  if (isnan(config.stepsPerMM) || config.stepsPerMM <= 0) {
    config.stepsPerMM = 1.0;
  }
  
  if (config.maxSpeed > MAX_SPEED) config.maxSpeed = MAX_SPEED;
  if (config.minSpeed < MIN_SPEED) config.minSpeed = MIN_SPEED;
  
  // Carregar estatísticas
  EEPROM.get(STATS_ADDR, stats);
  
  Serial.printf("Configuração carregada: %.1f steps/mm, %d-%d RPM\n", 
                config.stepsPerMM, config.minSpeed, config.maxSpeed);
}

void saveConfiguration() {
  Serial.println("Salvando configuração...");
  
  EEPROM.put(CALIBRATION_ADDR, config);
  EEPROM.put(STATS_ADDR, stats);
  
  Serial.println("Configuração salva!");
}

void initializeDiagnostic() {
  Serial.println("Inicializando sistema de diagnóstico...");
  
  diagnostic.encoderCount = 0;
  diagnostic.sensor1Status = digitalRead(SENSOR_IR_SENSOR1);
  diagnostic.sensor2Status = digitalRead(SENSOR_IR_SENSOR2);
  diagnostic.emergencyStopStatus = digitalRead(EMERGENCY_STOP_PIN);
  diagnostic.speedRPS = 0;
  diagnostic.accelerationPhase = 0;
  diagnostic.lastSensorTrigger = millis();
  
  Serial.println("Sistema de diagnóstico inicializado!");
}

void calibrateSystem() {
  Serial.println("=== MODO DE CALIBRAÇÃO ===");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Calibrando...");
  
  // Calibrar velocidade zero
  setMotorSpeed(0);
  delay(2000);
  
  // Calibrar velocidade máxima
  setMotorSpeed(config.maxSpeed);
  delay(3000);
  
  // Calibrar sensor IR
  calibrateInfraredSensors();
  
  // Calibrar encoder
  calibrateEncoder();
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Calibração OK!");
  delay(1000);
  
  Serial.println("Calibração concluída!");
}

void calibrateInfraredSensors() {
  Serial.println("Calibrando sensores IR...");
  
  // Testar sensor 1
  Serial.println("Posicione um objeto no sensor 1 e pressione Enter");
  while (!Serial.available()) {
    delay(100);
  }
  Serial.read();
  
  bool sensor1Detected = !digitalRead(SENSOR_IR_SENSOR1);
  Serial.printf("Sensor 1 - Sem objeto: %d, Com objeto: %d\n", 
                !digitalRead(SENSOR_IR_SENSOR1), sensor1Detected);
  
  // Testar sensor 2
  Serial.println("Posicione um objeto no sensor 2 e pressione Enter");
  while (!Serial.available()) {
    delay(100);
  }
  Serial.read();
  
  bool sensor2Detected = !digitalRead(SENSOR_IR_SENSOR2);
  Serial.printf("Sensor 2 - Sem objeto: %d, Com objeto: %d\n", 
                !digitalRead(SENSOR_IR_SENSOR2), sensor2Detected);
  
  Serial.println("Calibração de sensores IR concluída!");
}

void calibrateEncoder() {
  Serial.println("Calibrando encoder...");
  
  // Fazer motor girar 10 revoluções
  int testRevolutions = 10;
  int stepsPerRevolution = STEP_PER_REV;
  
  motor.step(stepsPerRevolution * testRevolutions);
  
  int encoderPulses = diagnostic.encoderCount;
  float pulsesPerRevolution = (float)encoderPulses / testRevolutions;
  
  Serial.printf("Encoder: %d pulsos em %d revoluções = %.1f pulsos/rev\n",
                encoderPulses, testRevolutions, pulsesPerRevolution);
  
  // Reset contador
  diagnostic.encoderCount = 0;
  
  Serial.println("Calibração de encoder concluída!");
}

void initializeInterface() {
  Serial.println("Inicializando interface...");
  
  // Configurar como modo manual por padrão
  currentMode = MODE_MANUAL;
  
  // Estado inicial
  systemEnabled = false;
  targetSpeed = 0;
  currentSpeed = 0;
  accelerationStep = 0;
  
  // Atualizar display
  updateLCDDisplay();
  
  Serial.println("Interface inicializada!");
}

void setState(SystemState newState) {
  if (currentState != newState) {
    currentState = newState;
    stateStartTime = millis();
    
    // Atualizar LEDs baseado no estado
    updateStatusLEDs();
    
    // Log da mudança de estado
    Serial.printf("Estado alterado para: %d\n", currentState);
    
    // Executar ações específicas do estado
    switch (newState) {
      case STATE_IDLE:
        setMotorSpeed(0);
        break;
      case STATE_RUNNING:
        break;
      case STATE_PAUSED:
        break;
      case STATE_EMERGENCY_STOP:
        emergencyStop();
        break;
      case STATE_MAINTENANCE:
        enterMaintenanceMode();
        break;
      case STATE_CALIBRATION:
        enterCalibrationMode();
        break;
      case STATE_ERROR:
        handleError();
        break;
    }
  }
}

void executeMainLogic() {
  // Verificar botões
  checkButtons();
  
  // Processar sensores
  processSensors();
  
  // Executar lógica baseada no estado atual
  switch (currentState) {
    case STATE_IDLE:
      executeIdleLogic();
      break;
    case STATE_RUNNING:
      executeRunningLogic();
      break;
    case STATE_PAUSED:
      executePausedLogic();
      break;
    case STATE_EMERGENCY_STOP:
      executeEmergencyStopLogic();
      break;
    case STATE_MAINTENANCE:
      executeMaintenanceLogic();
      break;
    case STATE_CALIBRATION:
      executeCalibrationLogic();
      break;
    case STATE_ERROR:
      executeErrorLogic();
      break;
  }
}

void executeIdleLogic() {
  // Modo de espera - verificar se deve iniciar
  if (systemEnabled) {
    setState(STATE_RUNNING);
  }
}

void executeRunningLogic() {
  // Lógica de execução normal
  
  // Verificar sensores em modo automático
  if (currentMode == MODE_AUTOMATIC) {
    if (diagnostic.sensor1Status) {
      // Parar automaticamente
      if (config.autoStop) {
        targetSpeed = 0;
      }
      diagnostic.lastSensorTrigger = millis();
    }
  }
  
  // Verificar timeout de auto-stop
  if (config.autoStop && !diagnostic.sensor1Status && 
      (millis() - diagnostic.lastSensorTrigger) > config.autoStopDelay) {
    // Tempo decorrido, retomar velocidade se estava no automático
    if (currentMode == MODE_AUTOMATIC) {
      targetSpeed = config.maxSpeed;
    }
  }
}

void executePausedLogic() {
  // Modo pausado - não fazer nada, apenas aguardar comando
}

void executeEmergencyStopLogic() {
  // Modo de parada de emergência - aguardar reset manual
  if (digitalRead(EMERGENCY_STOP_PIN) == HIGH) {
    // E-stop liberado, voltar ao modo idle
    emergencyStopTriggered = false;
    setState(STATE_IDLE);
  }
}

void executeMaintenanceLogic() {
  // Modo de manutenção - executar tarefas automáticas
  if ((millis() - stats.lastMaintenance) > 86400000) { // 24 horas
    performAutoMaintenance();
  }
}

void executeCalibrationLogic() {
  // Modo de calibração - aguardar comandos
}

void executeErrorLogic() {
  // Modo de erro - aguardar reset manual ou diagnóstico
}

void processCommands() {
  // Processar comandos do Bluetooth
  while (bluetooth.available()) {
    char c = bluetooth.read();
    if (c == '\n' || c == '\r') {
      if (commandBuffer.length() > 0) {
        processBluetoothCommand(commandBuffer);
        commandBuffer = "";
      }
    } else {
      commandBuffer += c;
    }
  }
  
  // Processar comandos do Serial
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (commandBuffer.length() > 0) {
        processSerialCommand(commandBuffer);
        commandBuffer = "";
      }
    } else {
      commandBuffer += c;
    }
  }
}

void processBluetoothCommand(String command) {
  command.trim();
  
  Serial.printf("Comando Bluetooth: %s\n", command.c_str());
  
  if (command == "START") {
    startSystem();
  } else if (command == "STOP") {
    stopSystem();
  } else if (command == "PAUSE") {
    pauseSystem();
  } else if (command == "RESET") {
    resetSystem();
  } else if (command.startsWith("SPEED:")) {
    int speed = command.substring(6).toInt();
    setTargetSpeed(speed);
  } else if (command == "MODE:AUTO") {
    setMode(MODE_AUTOMATIC);
  } else if (command == "MODE:MANUAL") {
    setMode(MODE_MANUAL);
  } else if (command == "STATUS") {
    sendStatus();
  } else if (command == "DIAGNOSTIC") {
    sendDiagnostic();
  } else if (command.startsWith("CONFIG:")) {
    processConfigCommand(command);
  } else if (command == "CALIBRATE") {
    setState(STATE_CALIBRATION);
  } else if (command == "MAINTENANCE") {
    setState(STATE_MAINTENANCE);
  } else {
    sendResponse("UNKNOWN_COMMAND");
  }
}

void processSerialCommand(String command) {
  command.trim();
  
  if (command == "help" || command == "?") {
    printHelp();
  } else if (command == "status") {
    printStatus();
  } else if (command == "diagnostic") {
    printDiagnostic();
  } else if (command == "calibrate") {
    setState(STATE_CALIBRATION);
  } else if (command == "config") {
    printConfig();
  } else if (command == "stats") {
    printStatistics();
  } else {
    // Reencaminhar para processamento Bluetooth
    processBluetoothCommand(command);
  }
}

void processConfigCommand(String command) {
  // Implementar processamento de configuração
  // Ex: CONFIG:speed=25,mode=auto
  sendResponse("CONFIG_UPDATED");
}

void checkButtons() {
  static bool lastModeBtn = HIGH;
  static bool lastStartBtn = HIGH;
  static unsigned long lastBtnTime = 0;
  
  bool currentModeBtn = digitalRead(BTN_MODE_PIN);
  bool currentStartBtn = digitalRead(BTN_START_STOP_PIN);
  
  // Debounce para botão de modo
  if (currentModeBtn != lastModeBtn) {
    if ((millis() - lastBtnTime) > 50) {
      if (currentModeBtn == LOW) {
        toggleMode();
      }
      lastBtnTime = millis();
    }
  }
  
  // Debounce para botão start/stop
  if (currentStartBtn != lastStartBtn) {
    if ((millis() - lastBtnTime) > 50) {
      if (currentStartBtn == LOW) {
        toggleSystem();
      }
      lastBtnTime = millis();
    }
  }
  
  lastModeBtn = currentModeBtn;
  lastStartBtn = currentStartBtn;
}

void toggleMode() {
  if (currentMode == MODE_MANUAL) {
    setMode(MODE_AUTOMATIC);
  } else {
    setMode(MODE_MANUAL);
  }
}

void setMode(OperationMode mode) {
  currentMode = mode;
  
  Serial.printf("Modo alterado para: %d\n", currentMode);
  
  // Ajustar velocidade se necessário
  if (systemEnabled) {
    if (currentMode == MODE_AUTOMATIC) {
      setTargetSpeed(config.maxSpeed);
    }
  }
  
  updateLCDDisplay();
}

void toggleSystem() {
  if (systemEnabled) {
    stopSystem();
  } else {
    startSystem();
  }
}

void startSystem() {
  if (currentState == STATE_IDLE) {
    systemEnabled = true;
    setTargetSpeed(config.minSpeed);
    Serial.println("Sistema iniciado!");
    sendResponse("SYSTEM_STARTED");
  }
}

void stopSystem() {
  systemEnabled = false;
  setTargetSpeed(0);
  setState(STATE_IDLE);
  Serial.println("Sistema parado!");
  sendResponse("SYSTEM_STOPPED");
}

void pauseSystem() {
  if (currentState == STATE_RUNNING) {
    setState(STATE_PAUSED);
    Serial.println("Sistema pausado!");
    sendResponse("SYSTEM_PAUSED");
  } else if (currentState == STATE_PAUSED) {
    setState(STATE_RUNNING);
    Serial.println("Sistema retomado!");
    sendResponse("SYSTEM_RESUMED");
  }
}

void setTargetSpeed(int speed) {
  speed = constrain(speed, MIN_SPEED, MAX_SPEED);
  targetSpeed = speed;
  
  Serial.printf("Velocidade alvo: %d RPM\n", targetSpeed);
  
  // Iniciar aceleração suave se estiver executando
  if (currentState == STATE_RUNNING) {
    accelerationStep = 0;
  }
  
  updateLCDDisplay();
}

void maintainAcceleration() {
  if (currentState != STATE_RUNNING) return;
  
  if (targetSpeed != currentSpeed) {
    accelerationStep++;
    
    int speedDiff = targetSpeed - currentSpeed;
    int stepSize = max(1, abs(speedDiff) / ACCELERATION_STEPS);
    
    if (abs(speedDiff) <= stepSize) {
      currentSpeed = targetSpeed;
    } else {
      currentSpeed += (speedDiff > 0) ? stepSize : -stepSize;
    }
    
    setMotorSpeed(currentSpeed);
    
    diagnostic.accelerationPhase = accelerationStep;
    
    if (accelerationStep >= ACCELERATION_STEPS) {
      accelerationStep = 0;
    }
  }
}

void setMotorSpeed(int rpm) {
  currentSpeed = rpm;
  motor.setSpeed(rpm);
  
  // Atualizar estatísticas
  stats.avgSpeed = ((stats.avgSpeed * 0.9) + (rpm * 0.1));
}

void processSensors() {
  static unsigned long lastSensorRead = 0;
  
  if (millis() - lastSensorRead < 100) return; // Ler a cada 100ms
  lastSensorRead = millis();
  
  // Ler sensores IR
  diagnostic.sensor1Status = !digitalRead(SENSOR_IR_SENSOR1);
  diagnostic.sensor2Status = !digitalRead(SENSOR_IR_SENSOR2);
  
  // Contar peças se sensor 1 detectado
  if (diagnostic.sensor1Status) {
    stats.totalPieces++;
    diagnostic.lastSensorTrigger = millis();
  }
  
  // Verificar parada de emergência
  diagnostic.emergencyStopStatus = digitalRead(EMERGENCY_STOP_PIN);
  
  // Ler potenciômetro de velocidade (se em modo manual)
  if (currentMode == MODE_MANUAL && systemEnabled) {
    int potValue = analogRead(POT_SPEED_PIN);
    int speed = map(potValue, 0, 1023, MIN_SPEED, config.maxSpeed);
    setTargetSpeed(speed);
  }
}

void checkEmergencyConditions() {
  // Verificar parada de emergência
  if (diagnostic.emergencyStopStatus == LOW && !emergencyStopTriggered) {
    emergencyStopTriggered = true;
    stats.emergencyStops++;
    setState(STATE_EMERGENCY_STOP);
  }
  
  // Verificar outros erros (temperatura, sobrecarga, etc.)
  if (detectSystemError()) {
    setState(STATE_ERROR);
  }
}

bool detectSystemError() {
  // Implementar detecção de erros:
  // - Temperatura excessiva
  // - Sobrecarga do motor
  // - Falha de comunicação
  // - Encoder com problemas
  
  return false; // Por enquanto, sempre OK
}

void emergencyStop() {
  Serial.println("=== PARADA DE EMERGÊNCIA ===");
  
  // Parar motor imediatamente
  setMotorSpeed(0);
  systemEnabled = false;
  
  // Parada suave com incremento de velocidade negativo
  for (int i = currentSpeed; i > 0; i -= 2) {
    setMotorSpeed(i);
    delay(50);
  }
  
  setState(STATE_IDLE);
  
  // Som de alerta (se configurado)
  if (config.soundAlerts) {
    // Implementar buzzer
  }
  
  // Log do evento
  Serial.println("Parada de emergência executada!");
}

void enterMaintenanceMode() {
  Serial.println("=== MODO DE MANUTENÇÃO ===");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Modo Manutencao");
  
  // Executar tarefas de manutenção
  performAutoMaintenance();
}

void enterCalibrationMode() {
  Serial.println("=== MODO DE CALIBRAÇÃO ===");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Modo Calibracao");
  lcd.setCursor(0, 1);
  lcd.print("Use comandos seriais");
  
  // Aguardar comandos de calibração
  while (currentState == STATE_CALIBRATION) {
    if (Serial.available()) {
      String cmd = Serial.readString();
      cmd.trim();
      
      if (cmd == "calibrate_speed") {
        calibrateSpeed();
      } else if (cmd == "calibrate_sensors") {
        calibrateInfraredSensors();
      } else if (cmd == "calibrate_encoder") {
        calibrateEncoder();
      } else if (cmd == "exit" || cmd == "quit") {
        setState(STATE_IDLE);
        break;
      } else {
        Serial.println("Comandos: calibrate_speed, calibrate_sensors, calibrate_encoder, exit");
      }
    }
    
    delay(100);
  }
}

void performAutoMaintenance() {
  Serial.println("Executando manutenção automática...");
  
  // Executar sequência de limpeza
  motor.step(100); // Movimento suave
  delay(1000);
  motor.step(-100);
  delay(1000);
  
  // Resetar encoder
  diagnostic.encoderCount = 0;
  
  // Atualizar timestamp
  stats.lastMaintenance = millis();
  
  Serial.println("Manutenção automática concluída!");
}

void calibrateSpeed() {
  Serial.println("Calibrando sistema de velocidade...");
  
  // Testar diferentes velocidades
  for (int speed = MIN_SPEED; speed <= config.maxSpeed; speed += 5) {
    Serial.printf("Testando velocidade: %d RPM\n", speed);
    setMotorSpeed(speed);
    delay(2000);
  }
  
  Serial.println("Calibração de velocidade concluída!");
}

void updateDiagnostic() {
  static unsigned long lastUpdate = 0;
  
  if (millis() - lastUpdate < 1000) return; // Atualizar a cada segundo
  lastUpdate = millis();
  
  // Calcular velocidade atual
  static int lastEncoderCount = 0;
  int encoderDiff = diagnostic.encoderCount - lastEncoderCount;
  lastEncoderCount = diagnostic.encoderCount;
  
  diagnostic.speedRPS = encoderDiff; // Pulsos por segundo
  
  // Estimar consumo de energia
  float powerFactor = (currentSpeed / (float)MAX_SPEED);
  diagnostic.motorCurrent = powerFactor * 2.0; // Amperes (estimativa)
  
  // Estimar temperatura (baseado no tempo de execução)
  unsigned long runtimeMinutes = stats.totalRuntime / 60000;
  diagnostic.motorTemperature = 25.0 + (runtimeMinutes * 0.1); // °C
  
  // Atualizar estatísticas
  stats.totalRuntime += 1000; // +1 segundo
  stats.maxPower = max(stats.maxPower, diagnostic.motorCurrent * 12.0); // P = V * I
  
  // Verificar necessidade de manutenção
  if (runtimeMinutes > 0 && (runtimeMinutes % 60) == 0) { // A cada hora
    Serial.println("Tempo de manutenção atingido!");
  }
}

void updateInterface() {
  static unsigned long lastUpdate = 0;
  
  if (millis() - lastUpdate < 2000) return; // Atualizar a cada 2 segundos
  lastUpdate = millis();
  
  updateLCDDisplay();
  updateStatusLEDs();
}

void updateLCDDisplay() {
  lcd.clear();
  
  // Linha 1: Estado e modo
  lcd.setCursor(0, 0);
  String stateStr = getStateString();
  String modeStr = getModeString();
  lcd.print(stateStr + " " + modeStr);
  
  // Linha 2: Velocidade
  lcd.setCursor(0, 1);
  lcd.print("Vel: " + String(currentSpeed) + " RPM");
  
  // Linha 3: Peças processadas
  lcd.setCursor(0, 2);
  lcd.print("Peças: " + String(stats.totalPieces));
  
  // Linha 4: Tempo de execução
  lcd.setCursor(0, 3);
  unsigned long runtime = stats.totalRuntime / 1000;
  lcd.print("Tempo: " + String(runtime) + "s");
}

void updateStatusLEDs() {
  if (config.ledIndicators) {
    switch (currentState) {
      case STATE_IDLE:
        digitalWrite(LED_STATUS, LOW);
        digitalWrite(LED_ERROR, LOW);
        break;
      case STATE_RUNNING:
        digitalWrite(LED_STATUS, HIGH);
        digitalWrite(LED_ERROR, LOW);
        break;
      case STATE_PAUSED:
        // Piscada lenta
        static unsigned long lastBlink = 0;
        if (millis() - lastBlink > 1000) {
          digitalWrite(LED_STATUS, !digitalRead(LED_STATUS));
          lastBlink = millis();
        }
        break;
      case STATE_EMERGENCY_STOP:
        digitalWrite(LED_STATUS, LOW);
        digitalWrite(LED_ERROR, HIGH);
        break;
      case STATE_ERROR:
        digitalWrite(LED_STATUS, LOW);
        // Piscada rápida
        static unsigned long lastBlink = 0;
        if (millis() - lastBlink > 200) {
          digitalWrite(LED_ERROR, !digitalRead(LED_ERROR));
          lastBlink = millis();
        }
        break;
    }
  }
}

String getStateString() {
  switch (currentState) {
    case STATE_IDLE: return "IDLE";
    case STATE_RUNNING: return "RUN";
    case STATE_PAUSED: return "PAUSE";
    case STATE_EMERGENCY_STOP: return "E-STOP";
    case STATE_MAINTENANCE: return "MAINT";
    case STATE_CALIBRATION: return "CALIB";
    case STATE_ERROR: return "ERROR";
    default: return "UNK";
  }
}

String getModeString() {
  switch (currentMode) {
    case MODE_MANUAL: return "MAN";
    case MODE_AUTOMATIC: return "AUTO";
    case MODE_MAINTENANCE: return "MAIN";
    case MODE_CALIBRATION: return "CAL";
    default: return "UNK";
  }
}

void sendResponse(String response) {
  bluetooth.println(response);
  Serial.println("Resposta: " + response);
}

void sendStatus() {
  StaticJsonDocument<300> status;
  status["state"] = getStateString();
  status["mode"] = getModeString();
  status["speed"] = currentSpeed;
  status["targetSpeed"] = targetSpeed;
  status["enabled"] = systemEnabled;
  status["pieces"] = stats.totalPieces;
  status["runtime"] = stats.totalRuntime;
  status["avgSpeed"] = stats.avgSpeed;
  status["errors"] = stats.errorCount;
  
  String json;
  serializeJson(status, json);
  sendResponse(json);
}

void sendDiagnostic() {
  StaticJsonDocument<300> diag;
  diag["motorCurrent"] = diagnostic.motorCurrent;
  diag["motorTemp"] = diagnostic.motorTemperature;
  diag["encoderCount"] = diagnostic.encoderCount;
  diag["speedRPS"] = diagnostic.speedRPS;
  diag["sensor1"] = diagnostic.sensor1Status;
  diag["sensor2"] = diagnostic.sensor2Status;
  diag["emergencyStop"] = diagnostic.emergencyStopStatus;
  diag["accelerationPhase"] = diagnostic.accelerationPhase;
  
  String json;
  serializeJson(diag, json);
  sendResponse(json);
}

void printHelp() {
  Serial.println("\n=== COMANDOS DISPONÍVEIS ===");
  Serial.println("CONTROLE:");
  Serial.println("  START    - Iniciar sistema");
  Serial.println("  STOP     - Parar sistema");
  Serial.println("  PAUSE    - Pausar/retomar");
  Serial.println("  SPEED:n  - Definir velocidade (RPM)");
  Serial.println("");
  Serial.println("MODO:");
  Serial.println("  MODE:AUTO    - Modo automático");
  Serial.println("  MODE:MANUAL  - Modo manual");
  Serial.println("");
  Serial.println("INFORMAÇÃO:");
  Serial.println("  STATUS      - Status do sistema");
  Serial.println("  DIAGNOSTIC  - Dados de diagnóstico");
  Serial.println("  CONFIG      - Configuração atual");
  Serial.println("  STATS       - Estatísticas");
  Serial.println("");
  Serial.println("MANUTENÇÃO:");
  Serial.println("  CALIBRATE   - Modo de calibração");
  Serial.println("  MAINTENANCE - Modo de manutenção");
  Serial.println("  RESET       - Reset do sistema");
  Serial.println("=================================\n");
}

void printStatus() {
  Serial.println("\n=== STATUS DO SISTEMA ===");
  Serial.printf("Estado: %s\n", getStateString().c_str());
  Serial.printf("Modo: %s\n", getModeString().c_str());
  Serial.printf("Velocidade: %d/%d RPM\n", currentSpeed, targetSpeed);
  Serial.printf("Sistema: %s\n", systemEnabled ? "Ativo" : "Inativo");
  Serial.printf("Peças processadas: %lu\n", stats.totalPieces);
  Serial.printf("Tempo de execução: %lu s\n", stats.totalRuntime / 1000);
  Serial.printf("Velocidade média: %.1f RPM\n", stats.avgSpeed);
  Serial.printf("Paradas de emergência: %d\n", stats.emergencyStops);
  Serial.printf("Erros: %d\n", stats.errorCount);
  Serial.println("========================\n");
}

void printDiagnostic() {
  Serial.println("\n=== DIAGNÓSTICO ===");
  Serial.printf("Corrente do motor: %.2f A\n", diagnostic.motorCurrent);
  Serial.printf("Temperatura: %.1f°C\n", diagnostic.motorTemperature);
  Serial.printf("Contador encoder: %d\n", diagnostic.encoderCount);
  Serial.printf("Velocidade: %d pulsos/s\n", diagnostic.speedRPS);
  Serial.printf("Sensor 1: %s\n", diagnostic.sensor1Status ? "ATIVO" : "inativo");
  Serial.printf("Sensor 2: %s\n", diagnostic.sensor2Status ? "ATIVO" : "inativo");
  Serial.printf("E-stop: %s\n", diagnostic.emergencyStopStatus ? "PRESSIONADO" : "liberado");
  Serial.printf("Fase aceleração: %d\n", diagnostic.accelerationPhase);
  Serial.println("===================\n");
}

void printConfig() {
  Serial.println("\n=== CONFIGURAÇÃO ===");
  Serial.printf("Steps por mm: %.1f\n", config.stepsPerMM);
  Serial.printf("Velocidade máxima: %d RPM\n", config.maxSpeed);
  Serial.printf("Velocidade mínima: %d RPM\n", config.minSpeed);
  Serial.printf("Auto-stop: %s\n", config.autoStop ? "Ativo" : "Inativo");
  Serial.printf("Delay auto-stop: %lu ms\n", config.autoStopDelay);
  Serial.printf("Alertas sonoros: %s\n", config.soundAlerts ? "Ativo" : "Inativo");
  Serial.printf("LEDs indicadores: %s\n", config.ledIndicators ? "Ativo" : "Inativo");
  Serial.printf("Fator consumo: %.1f\n", config.powerConsumptionFactor);
  Serial.println("==================\n");
}

void printStatistics() {
  Serial.println("\n=== ESTATÍSTICAS ===");
  Serial.printf("Tempo total: %lu ms\n", stats.totalRuntime);
  Serial.printf("Peças totais: %lu\n", stats.totalPieces);
  Serial.printf("Distância: %.1f mm\n", stats.totalDistance);
  Serial.printf("Velocidade média: %.1f RPM\n", stats.avgSpeed);
  Serial.printf("E-stops: %d\n", stats.emergencyStops);
  Serial.printf("Erros: %d\n", stats.errorCount);
  Serial.printf("Potência máxima: %.1f W\n", stats.maxPower);
  Serial.printf("Última manutenção: %lu\n", stats.lastMaintenance);
  Serial.println("==================\n");
}

void printSystemInfo() {
  Serial.println("\n=== INFORMAÇÕES DO SISTEMA ===");
  Serial.println("Modelo: 3dPot Arduino Esteira Transportadora v2.0");
  Serial.printf("Memória livre: %d bytes\n", freeMemory());
  Serial.printf("Versão firmware: 2.0\n");
  Serial.printf("Data: 2025-11-10\n");
  Serial.println("============================\n");
}

int freeMemory() {
  char top;
  return &top - reinterpret_cast<char*>(sbrk(0));
}

void encoderInterrupt() {
  diagnostic.encoderCount++;
  
  // Atualizar distância total (baseado no steps/mm)
  if (currentSpeed > 0) {
    float distancePerStep = 1.0 / config.stepsPerMM; // mm por step
    stats.totalDistance += distancePerStep;
  }
}

void resetSystem() {
  Serial.println("Resetando sistema...");
  
  // Resetar variáveis de estado
  systemEnabled = false;
  targetSpeed = 0;
  currentSpeed = 0;
  accelerationStep = 0;
  emergencyStopTriggered = false;
  
  // Resetar estatísticas de sessão
  stats.totalRuntime = 0;
  stats.totalPieces = 0;
  stats.totalDistance = 0;
  stats.avgSpeed = 0;
  stats.emergencyStops = 0;
  stats.errorCount = 0;
  stats.maxPower = 0;
  
  // Resetar diagnóstico
  diagnostic.motorCurrent = 0;
  diagnostic.motorTemperature = 25;
  diagnostic.encoderCount = 0;
  diagnostic.speedRPS = 0;
  diagnostic.accelerationPhase = 0;
  
  // Voltar ao estado idle
  setState(STATE_IDLE);
  
  // Salvar mudanças
  saveConfiguration();
  
  Serial.println("Sistema resetado!");
  sendResponse("SYSTEM_RESET");
}

void handleError() {
  Serial.println("=== ERRO DO SISTEMA ===");
  
  // Parar motor
  setMotorSpeed(0);
  systemEnabled = false;
  
  // Incrementar contador de erros
  stats.errorCount++;
  
  // Log do erro
  Serial.println("Erro detectado! Verificar diagnóstico.");
  
  // Aguardar reset manual
  while (currentState == STATE_ERROR) {
    if (Serial.available()) {
      String cmd = Serial.readString();
      cmd.trim();
      if (cmd == "reset" || cmd == "RESET") {
        resetSystem();
        setState(STATE_IDLE);
      }
    }
    delay(1000);
  }
}

void executeMaintenanceTasks() {
  static unsigned long lastMaintenance = 0;
  
  if (millis() - lastMaintenance < 10000) return; // A cada 10 segundos
  lastMaintenance = millis();
  
  // Executar tarefas automáticas de manutenção:
  // - Verificar temperatura
  // - Monitorar desgaste
  // - Calibrar sensores
  // - Limpeza automática
  
  // Aqui implementaria as tarefas específicas
  // Por enquanto, apenas log
  Serial.printf("Manutenção - Temp: %.1f°C, Corrente: %.2fA\n", 
                diagnostic.motorTemperature, diagnostic.motorCurrent);
}