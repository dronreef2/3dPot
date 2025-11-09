// Mini Esteira Transportadora Modular - Arduino
#include <AccelStepper.h>

// Pinos do motor de passo
const int STEP_PIN = 2;
const int DIR_PIN = 3;
const int ENABLE_PIN = 4;

// Pinos dos sensores
const int SENSOR_ENTRADA = 5;    // Sensor IR entrada
const int SENSOR_SAIDA = 6;      // Sensor IR saída
const int BOTAO_ACIONAMENTO = 7; // Botão para iniciar ciclo

// Pinos dos LEDs de status
const int LED_VERDE = 8;  // Peça detectada
const int LED_VERMELHO = 9; // Erro
const int LED_AMARELO = 10; // Em funcionamento

// Pinos do potenciômetro (controle de velocidade)
const int POT_VELOCIDADE = A0;

// Configuração do motor de passo
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// Variáveis de controle
bool sistemaAtivo = false;
bool objetoDetectado = false;
int velocidadeMotor = 500;  // Pulsos por segundo

void setup() {
  Serial.begin(9600);
  
  // Configura pinos
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(SENSOR_ENTRADA, INPUT_PULLUP);
  pinMode(SENSOR_SAIDA, INPUT_PULLUP);
  pinMode(BOTAO_ACIONAMENTO, INPUT_PULLUP);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_AMARELO, OUTPUT);
  
  // Configura motor de passo
  stepper.setMaxSpeed(1000.0);
  stepper.setAcceleration(500.0);
  stepper.setSpeed(velocidadeMotor);
  stepper.setEnablePin(ENABLE_PIN);
  stepper.setPinsInverted(false, false, true); // Enable low true = enable
  
  // Estado inicial
  sistemaAtivo = false;
  stopMotor();
  updateLEDs();
  
  Serial.println("Mini Esteira Transportadora Inicializada");
  Serial.println("Pressione o botão para iniciar o sistema");
}

void loop() {
  // Atualiza velocidade baseada no potenciômetro
  updateVelocity();
  
  // Monitora botões
  if (digitalRead(BOTAO_ACIONAMENTO) == LOW) {
    delay(50); // Debounce
    if (digitalRead(BOTAO_ACIONAMENTO) == LOW) {
      toggleSistema();
    }
  }
  
  if (sistemaAtivo) {
    handleSensors();
    runMotor();
  } else {
    stopMotor();
  }
  
  // Atualiza LEDs
  updateLEDs();
  
  // Log periódico
  static unsigned long lastLog = 0;
  if (millis() - lastLog > 2000) {
    logStatus();
    lastLog = millis();
  }
}

void toggleSistema() {
  sistemaAtivo = !sistemaAtivo;
  if (!sistemaAtivo) {
    objetoDetectado = false;
  }
  Serial.println(sistemaAtivo ? "Sistema ATIVADO" : "Sistema DESATIVADO");
}

void handleSensors() {
  bool entradaDetectada = (digitalRead(SENSOR_ENTRADA) == LOW);
  bool saidaDetectada = (digitalRead(SENSOR_SAIDA) == LOW);
  
  // Detecta objeto na entrada
  if (entradaDetectada && !objetoDetectado) {
    objetoDetectado = true;
    Serial.println("Objeto detectado na entrada");
    
    // Para o motor para aguardar posicionamento
    stepper.stop();
  }
  
  // Detecta objeto na saída
  if (saidaDetectada && objetoDetectado) {
    objetoDetectado = false;
    Serial.println("Objeto chegou ao destino");
    
    // Para o motor
    stepper.stop();
    
    // Aciona próxima etapa (ex: braço robótico)
    acionarProximaEtapa();
  }
}

void acionarProximaEtapa() {
  Serial.println("ACIONANDO PRÓXIMA ETAPA");
  
  // Aqui você pode adicionar código para:
  // - Acionar um servo motor
  // - Enviar sinal para outro Arduino
  // - Acionar uma bomba pneumática
  // - Etc.
  
  // Exemplo: acender LED verde por 2 segundos
  digitalWrite(LED_VERDE, HIGH);
  delay(2000);
  digitalWrite(LED_VERDE, LOW);
}

void runMotor() {
  // Só executa se não há objeto detectado na entrada
  if (!objetoDetectado) {
    stepper.run();
  }
}

void stopMotor() {
  stepper.stop();
  // Mantém o enable ativo para segurar posição
  // stepper.disableOutputs(); // Desabilita se quiser economizar energia
}

void updateVelocity() {
  int potValue = analogRead(POT_VELOCIDADE);
  // Mapeia de 0-1023 para 100-1000 pulsos/s
  velocidadeMotor = map(potValue, 0, 1023, 100, 1000);
  stepper.setSpeed(velocidadeMotor);
}

void updateLEDs() {
  // LED Amarelo: sistema ativo
  digitalWrite(LED_AMARELO, sistemaAtivo ? HIGH : LOW);
  
  // LED Vermelho: erro ou sistema inativo
  digitalWrite(LED_VERMELHO, (!sistemaAtivo || objetoDetectado) ? HIGH : LOW);
  
  // LED Verde: objeto detectado (ativo)
  digitalWrite(LED_VERDE, objetoDetectado ? HIGH : LOW);
}

void logStatus() {
  Serial.println("=== STATUS DA ESTEIRA ===");
  Serial.printf("Sistema: %s\n", sistemaAtivo ? "ATIVO" : "INATIVO");
  Serial.printf("Objeto detectado: %s\n", objetoDetectado ? "SIM" : "NÃO");
  Serial.printf("Velocidade: %d pulsos/s\n", velocidadeMotor);
  Serial.printf("Posição motor: %d\n", stepper.currentPosition());
  Serial.printf("Sensor entrada: %s\n", digitalRead(SENSOR_ENTRADA) == LOW ? "ATIVO" : "INATIVO");
  Serial.printf("Sensor saída: %s\n", digitalRead(SENSOR_SAIDA) == LOW ? "ATIVO" : "INATIVO");
  Serial.println("========================");
}

// Funções de segurança
void emergencia() {
  sistemaAtivo = false;
  stopMotor();
  digitalWrite(LED_VERMELHO, HIGH);
  Serial.println("*** EMERGÊNCIA ATIVADA ***");
  
  // Aguarda botão ser solto
  while (digitalRead(BOTAO_ACIONAMENTO) == LOW) {
    delay(100);
  }
  
  digitalWrite(LED_VERMELHO, LOW);
  Serial.println("Sistema resetado. Pressione botão para reativar.");
}

// Função para calibração do motor
void calibrarMotor() {
  Serial.println("Iniciando calibração do motor...");
  
  // Move para posição zero
  stepper.moveTo(0);
  while (stepper.isRunning()) {
    stepper.run();
  }
  
  // Move 1000 passos para frente
  stepper.moveTo(1000);
  while (stepper.isRunning()) {
    stepper.run();
  }
  
  // Volta à posição zero
  stepper.moveTo(0);
  while (stepper.isRunning()) {
    stepper.run();
  }
  
  Serial.println("Calibração concluída");
}
