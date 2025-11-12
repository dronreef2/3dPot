/*
 * 3dPot Arduino Conveyor Belt - Template de Configuração
 * 
 * INSTRUÇÕES:
 * 1. Copie este arquivo para 'config.h'
 * 2. Ajuste as configurações abaixo com seus valores reais
 * 3. NUNCA comite o arquivo config.h no git
 */

#ifndef CONFIG_H
#define CONFIG_H

// ================================
// MOTOR DE PASSO (DRIVER)
// ================================
// Pinos conectados ao driver de motor de passo (A4988, DRV8825, etc.)
#define STEP_PIN 2
#define DIR_PIN 3
#define ENABLE_PIN 4

// Configuração do motor
#define MOTOR_STEPS_PER_REV 200        // 1.8° por passo = 200 passos/rev
#define MOTOR_MICROSTEPS 16            // Microstepping (1, 2, 4, 8, 16)
#define MAX_SPEED 1000.0               // Pulsos por segundo (máximo)
#define ACCELERATION 500.0             // Aceleração (pulsos/s²)
#define START_SPEED 200.0              // Velocidade inicial

// Posições (em passos)
#define HOME_POSITION 0
#define WORK_POSITION 1000
#define CLEANUP_POSITION 500

// ================================
// SENSORES
// ================================
// Pinos dos sensores (ativados em LOW)
#define SENSOR_ENTRADA 5    // Sensor IR entrada da peça
#define SENSOR_SAIDA 6      // Sensor IR saída da peça
#define EMERGENCIA_PIN 7    // Botão de emergência

// Configurações dos sensores
#define SENSOR_DEBOUNCE_MS 50      // Debounce para evitar ruído
#define SENSOR_TIMEOUT_MS 5000     // Timeout se peça não chegar

// ================================
// INTERFACE USUÁRIO
// ================================
// LEDs de status
#define LED_VERDE 8       // Peça detectada / Sucesso
#define LED_VERMELHO 9    // Erro / Emergencia
#define LED_AMARELO 10    // Em funcionamento / Warning

// Botões
#define BOTAO_START 11    // Botão iniciar/parar sistema
#define BOTAO_RESET 12    // Botão reset de emergência

// Potenciômetro para controle de velocidade
#define POT_VELOCIDADE A0
#define POT_MIN_SPEED 100    // Velocidade mínima (pulsos/s)
#define POT_MAX_SPEED 1000   // Velocidade máxima (pulsos/s)

// ================================
// COMUNICAÇÃO
// ================================
// Serial (para debug e comandos)
#define SERIAL_BAUDRATE 115200
#define SERIAL_TIMEOUT_MS 1000

// Communication protocols (future expansion)
#define I2C_ENABLED false
#define I2C_ADDRESS 0x42

#define SPI_ENABLED false

// ================================
// COMPORTAMENTO DO SISTEMA
// ================================
// Estados da máquina
#define AUTO_MODE true        // Modo automático (sem supervisão)
#define MANUAL_MODE false     // Modo manual (com intervenção)

// Timing
#define LOG_INTERVAL_MS 2000      // Intervalo entre logs de status
#define HEARTBEAT_INTERVAL_MS 500 // Intervalo do LED de heartbeat

// Ações automáticas
#define AUTO_REVERSE false        // Reversão automática após timeout
#define AUTO_CLEANUP true         // Limpeza automática após ciclo
#define BEEP_ON_SUCCESS true      // Beep sonoro em caso de sucesso

// ================================
// SEGURANÇA
// ================================
// Parâmetros de segurança
#define MAX_RUNTIME_MS 300000     // 5 minutos máximo de operação contínua
#define EMERGENCY_TIMEOUT_MS 3000 // 3 segundos para emergency stop
#define SENSOR_FAILURE_LIMIT 3    // Limite de falhas do sensor antes de parar

// Configurações de proteção
#define WDT_TIMEOUT_MS 8000       // Watchdog timeout
#define TEMP_SENSOR_PIN A1        // Pino do sensor de temperatura (opcional)
#define MAX_TEMP_C 80.0           // Temperatura máxima antes de parar

// ================================
// LOGGING E DEBUG
// ================================
// Níveis de log
#define DEBUG_LEVEL 1             // 0=Off, 1=Basic, 2=Verbose, 3=Debug
#define LOG_SENSOR_READINGS false // Log individual das leituras dos sensores
#define LOG_MOTOR_STATUS false    // Log detalhado do status do motor
#define PERFORMANCE_MONITOR true  // Monitor de performance

// Estatísticas
#define TRACK_CYCLES true         // Contar ciclos realizados
#define TRACK_UPTIME true         // Tempo de funcionamento
#define TRACK_ERRORS true         // Contar erros

// ================================
// CONFIGURAÇÕES AVANÇADAS
// ================================
// Buffer de comandos (para expansões futuras)
#define COMMAND_BUFFER_SIZE 10
#define COMMAND_TIMEOUT_MS 5000

// Pinos reservados para expansões
#define EXP_PIN_1 13    // Pino disponível para expansões
#define EXP_PIN_2 A2    // Pino disponível para expansões
#define EXP_PIN_3 A3    // Pino disponível para expansões
#define EXP_PIN_4 A4    // Pino disponível para expansões

// ================================
// CALIBRAÇÃO
// ================================
// Parâmetros de calibração
#define CALIBRATION_SPEED 200     // Velocidade para calibração
#define CALIBRATION_STEPS 1000    // Passos para calibração completa
#define HOMING_SPEED 100          // Velocidade para homing
#define HOMING_DIRECTION -1       // -1 = anti-horário, 1 = horário

#endif // CONFIG_H