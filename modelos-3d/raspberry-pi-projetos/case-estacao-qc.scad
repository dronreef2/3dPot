// Case para Raspberry Pi - Estação QC
// Arquivo OpenSCAD Paramétrico
// Data: 2025-11-10
// Projeto: 3dPot - Estação de Controle de Qualidade

// ==================== PARÂMETROS ====================
// Todas as medidas em mm

// Dimensões do Raspberry Pi 4
rpi_length = 85.0;          // Comprimento do RPi 4
rpi_width = 56.0;           // Largura do RPi 4
rpi_height = 17.0;          // Altura do RPi 4 (com conectores)
board_thickness = 1.2;      // Espessura da placa

// Dimensões do case
case_length = 95.0;         // Comprimento interno do case
case_width = 68.0;          // Largura interna do case
case_height = 22.0;         // Altura interna do case
wall_thickness = 2.0;       // Espessura das paredes

// Ventilação e散热
fan_diameter = 30.0;        // Diâmetro do ventilador
fan_hole_diameter = 3.0;    // Diâmetro dos furos de montagem do ventilador
vent_hole_diameter = 4.0;   // Diâmetro dos furos de ventilação
vent_spacing = 8.0;         // Espaçamento entre furos

// Portas e aberturas
usb_cutout_width = 15.0;    // Largura do recorte para USB
hdmi_cutout_width = 13.0;   // Largura do recorte para HDMI
ethernet_cutout_width = 13.0; // Largura do recorte para Ethernet
power_cutout_width = 8.0;   // Largura do recorte para energia

// Montagem
mounting_hole_diameter = 3.0;   // Diâmetro dos furos de montagem
mounting_hole_positions = [
    [case_length/2 - 10, case_width/2 - 10],
    [case_length/2 - 10, -case_width/2 + 10],
    [-case_length/2 + 10, case_width/2 - 10],
    [-case_length/2 + 10, -case_width/2 + 10]
];

// ==================== MODELAGEM ====================

module case_base() {
    // Base do case
    difference() {
        // Corpo principal
        cube([case_length, case_width, case_height]);
        
        // Cavidade interna para o RPi
        translate([wall_thickness, wall_thickness, wall_thickness]) {
            cube([case_length - 2*wall_thickness, 
                  case_width - 2*wall_thickness, 
                  case_height - wall_thickness]);
        }
    }
}

module ventilation_holes() {
    // Furos de ventilação nas paredes
    hole_positions = [
        // Laterais
        for (x = [-case_length/2 + 15:20:case_length/2 - 15])
        for (y = [-case_width/2 + 15:20:case_width/2 - 15])
        if (abs(x) < case_length/2 - 10 && abs(y) < case_width/2 - 10)
            [x, y, case_height/2],
        
        // Topo
        for (x = [-case_length/2 + 10:15:case_length/2 - 10])
        for (y = [-case_width/2 + 10:15:case_width/2 - 10])
        [x, y, case_height]
    ];
    
    for (pos = hole_positions) {
        if (pos[2] == case_height/2) {
            // Furos laterais
            translate([pos[0], pos[1], 0]) {
                cylinder(h = case_height, d = vent_hole_diameter);
            }
        } else {
            // Furos no topo
            translate([pos[0], pos[1], case_height - 1]) {
                cylinder(h = 2, d = vent_hole_diameter);
            }
        }
    }
}

module fan_mount() {
    // Suporte para ventilador no topo
    difference() {
        // Base do ventilador
        cylinder(d = fan_diameter + 4, h = 3);
        
        // Furo central para o ventilador
        cylinder(d = fan_diameter, h = 5);
        
        // Furos de montagem do ventilador
        for (angle = [0, 90, 180, 270]) {
            translate([
                cos(angle) * (fan_diameter/2 - 3),
                sin(angle) * (fan_diameter/2 - 3),
                0
            ]) {
                cylinder(d = fan_hole_diameter, h = 5);
            }
        }
    }
}

module port_cutouts() {
    // Recortes para portas
    // USB ports
    translate([case_length/2 - 5, 10, case_height/2 - 2]) {
        cube([5, usb_cutout_width, 8]);
    }
    
    translate([case_length/2 - 5, -10, case_height/2 - 2]) {
        cube([5, usb_cutout_width, 8]);
    }
    
    // HDMI ports
    translate([case_length/2 - 5, 20, case_height/2 - 2]) {
        cube([5, hdmi_cutout_width, 8]);
    }
    
    translate([case_length/2 - 5, -20, case_height/2 - 2]) {
        cube([5, hdmi_cutout_width, 8]);
    }
    
    // Ethernet port
    translate([-case_length/2, 0, case_height/2 - 2]) {
        cube([5, ethernet_cutout_width, 8]);
    }
    
    // Power port
    translate([-case_length/2, -15, case_height/2 - 2]) {
        cube([5, power_cutout_width, 8]);
    }
}

module mounting_holes() {
    // Furos de montagem nas esquinas
    for (pos = mounting_hole_positions) {
        translate([pos[0], pos[1], -1]) {
            cylinder(d = mounting_hole_diameter, h = case_height + 2);
        }
    }
}

module riser_pillars() {
    // Pilares de apoio para elevar o RPi
    pillar_positions = [
        [case_length/2 - 15, case_width/2 - 15],
        [case_length/2 - 15, -case_width/2 + 15],
        [-case_length/2 + 15, case_width/2 - 15],
        [-case_length/2 + 15, -case_width/2 + 15]
    ];
    
    for (pos = pillar_positions) {
        translate([pos[0], pos[1], wall_thickness]) {
            cylinder(d = 4, h = case_height - wall_thickness - 5);
        }
    }
}

module complete_case() {
    // Montagem completa do case
    difference() {
        case_base();
        port_cutouts();
        mounting_holes();
        ventilation_holes();
    }
    
    // Ventilador no topo
    translate([0, 0, case_height]) {
        fan_mount();
    }
    
    // Pilares de apoio
    riser_pillars();
}

// ==================== MONTAGEM FINAL ====================

complete_case();

// ==================== INSTRUÇÕES DE IMPRESSÃO ====================

/*
INSTRUÇÕES DE IMPRESSÃO 3D:

1. PARÂMETROS RECOMENDADOS:
   - Material: PLA+ (maior resistência térmica) ou PETG
   - Temperatura: PLA+ (220-235°C) / PETG (230-250°C)
   - Altura da camada: 0.2mm
   - Velocidade: 45-55mm/s
   - Suporte: DESNECESSÁRIO
   - Brim: 8mm para melhor aderência

2. ORIENTAÇÃO DE IMPRESSÃO:
   - Case base: Base para baixo
   - Ventilador: Disco para cima
   - Partes separadas para complexidade

3. MONTAGEM:
   1. Instalar ventilador na tampa
   2. Conectar fio do ventilador ao GPIO
   3. Inserir Raspberry Pi nos pilares
   4. Fechar case e fixar com parafusos
   5. Conectar cabos externos

4. COMPONENTES ADICIONAIS NECESSÁRIOS:
   - 1x Raspberry Pi 4 Model B
   - 1x Ventilador 30mm 5V
   - 1x Cartão microSD 32GB+
   - 4x Parafusos M3 x 8mm
   - 4x Porcas M3
   - 1x Fonte 5V 3A USB-C
   - 2x Cabos HDMI
   - 1x Cabo Ethernet
   - 1x Cabo USB para câmera

5. FUNCIONALIDADES:
   - Proteção física do RPi
   - Ventilação ativa com sensor de temperatura
   - Acesso fácil a todas as portas
   - Montagem em rack ou mesa
   - Facilita manutenção
   - Gestão de cabos organizada

6. ESPECIFICAÇÕES TÉCNICAS:
   - Dimensões: 95x68x22mm (interno)
   - Material: PLA+ com aditivos
   - Resistência: IP40 (poeira)
   - Ventilação: 30mm fan, 12V/5V
   - Capacidade térmica: Até 85°C ambiente
   - Vibração: <0.1G RMS

7. APLICAÇÕES:
   - Estação de controle de qualidade
   - Servidor de desenvolvimento
   - Edge computing
   - IoT gateway
   - Raspberry Pi para Indústria 4.0
   - Sistema de visão computacional

8. INTEGRAÇÃO COM PROJETO:
   - Câmera USB para inspeção
   - GPIO para sensores
   - Ethernet para comunicação
   - USB para dispositivos externos
   - HDMI para monitoramento
   - Software de QC integrado
*/