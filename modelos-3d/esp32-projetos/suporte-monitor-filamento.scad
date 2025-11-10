// Suporte para Monitor de Filamento ESP32
// Arquivo OpenSCAD Paramétrico
// Data: 2025-11-10
// Projeto: 3dPot - Monitor de Filamento WiFi

// ==================== PARÂMETROS ====================
// Todas as medidas em mm

// Dimensões do ESP32
esp32_width = 25.0;      // Largura do ESP32
esp32_length = 55.0;     // Comprimento do ESP32
esp32_height = 3.2;      // Altura do ESP32

// Dimensões do suporte base
base_width = 35.0;       // Largura da base
base_length = 70.0;      // Comprimento da base
base_height = 3.0;       // Altura da base

// Dimensões dos pinos de fixação
pin_diameter = 3.0;      // Diâmetro dos pinos
pin_height = 8.0;        // Altura dos pinos
pin_spacing_x = 20.0;    // Espaçamento entre pinos (eixo X)
pin_spacing_y = 45.0;    // Espaçamento entre pinos (eixo Y)

// Dimensões do alojamento do sensor
sensor_hole_diameter = 8.0;    // Diâmetro do furo do sensor
sensor_hole_depth = 5.0;       // Profundidade do furo do sensor

// Parâmetros de impressão
layer_height = 0.2;            // Altura da camada
wall_thickness = 1.2;          // Espessura da parede
bottom_thickness = 2.0;        // Espessura da base

// ==================== MODELAGEM ====================

module base_support() {
    // Base principal do suporte
    difference() {
        // Base sólida
        cube([base_width, base_length, base_height]);
        
        // Furo central para o ESP32
        translate([base_width/2, base_length/2, -1])
            cylinder(h = base_height + 2, d = esp32_width + 2);
    }
}

module mounting_pins() {
    // Posições dos pinos de fixação
    pin_positions = [
        [-pin_spacing_x/2, -pin_spacing_y/2, 0],
        [pin_spacing_x/2, -pin_spacing_y/2, 0],
        [-pin_spacing_x/2, pin_spacing_y/2, 0],
        [pin_spacing_x/2, pin_spacing_y/2, 0]
    ];
    
    for (pos = pin_positions) {
        translate([pos[0] + base_width/2, pos[1] + base_length/2, 0]) {
            // Pino cilíndrico
            cylinder(h = pin_height, d = pin_diameter);
            
            // Cabeça do pino (fita dupla face)
            translate([0, 0, pin_height - 1])
                cylinder(h = 1, d = pin_diameter + 2);
        }
    }
}

module sensor_housing() {
    // Alojamento para o sensor de peso
    translate([base_width/2 + esp32_width/2, base_length/2, -sensor_hole_depth]) {
        difference() {
            // Alojamento sólido
            cylinder(h = sensor_hole_depth + 5, d = sensor_hole_diameter + 2);
            
            // Furo para o sensor
            translate([0, 0, -1])
                cylinder(h = sensor_hole_depth + 7, d = sensor_hole_diameter);
        }
    }
}

module ventilation_holes() {
    // Furos de ventilação para o ESP32
    hole_positions = [
        [-10, 10, 0],
        [10, 10, 0],
        [-10, -10, 0],
        [10, -10, 0]
    ];
    
    for (pos = hole_positions) {
        translate([pos[0] + base_width/2, pos[1] + base_length/2, 0]) {
            cylinder(h = base_height + 2, d = 2);
        }
    }
}

// ==================== MONTAGEM FINAL ====================

// Base principal
base_support();

// Pinos de fixação
mounting_pins();

// Alojamento do sensor
sensor_housing();

// Furos de ventilação
ventilation_holes();

// ==================== INSTRUÇÕES DE IMPRESSÃO ====================

/*
INSTRUÇÕES DE IMPRESSÃO 3D:

1. PARÂMETROS RECOMENDADOS:
   - Material: PLA ou PETG
   - Temperatura: PLA (200-220°C) / PETG (220-250°C)
   - Altura da camada: 0.15-0.2mm
   - Velocidade: 50-60mm/s
   - Suporte: Desnecessário

2. ORIENTAÇÃO DE IMPRESSÃO:
   - Base para baixo, sem suporte
   - Pinos virados para cima

3. MONTAGEM:
   - Use fita dupla face nos pinos
   - Fixe o ESP32 centralmente
   - Posicione o sensor no alojamento
   - Use cola quentes se necessário

4. FUNCIONALIDADES:
   - Base estável para o ESP32
   - Pinos de fixação seguros
   - Alojamento para sensor de peso
   - Ventilação para resfriar o ESP32
   - Dimensões otimizadas para impressão

5. COMPATIBILIDADE:
   - ESP32 DevKit v1
   - Sensores de peso HX711
   - Display OLED 0.96"
   - Sensores de temperatura DHT22
*/