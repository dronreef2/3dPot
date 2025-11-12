// 3dPot Universal Case - Modelo 3D Paramétrico Avançado
// Projeto: 3dPot - Cases Paramétricos para Dispositivos
// Data: 2025-11-12
// Versão: 2.0
// Autor: MiniMax Agent

// ==================== PARÂMETROS CUSTOMIZÁVEIS ====================
// MODIFIQUE ESTAS VARIÁVEIS PARA PERSONALIZAR O MODELO

// Dimensões do dispositivo (em mm)
device_width = 30.0;      // Largura do dispositivo
device_length = 55.0;     // Comprimento do dispositivo  
device_height = 10.0;     // Altura do dispositivo

// Espessuras e folgas (em mm)
wall_thickness = 2.0;     // Espessura das paredes
base_thickness = 3.0;     // Espessura da base
clearance = 1.0;          // Folga ao redor do dispositivo
lid_gap = 0.5;            // Gap para tampa

// Tipo de tampa e fixação
lid_type = "snap";        // "snap", "screw", "hinge", "slide"
screw_holes = true;       // Incluir furos para parafusos M3
snap_tolerance = 0.2;     // Tolerância para snap fits (mm)

// Ventilação e refrigeração
ventilation_enabled = true;      // Habilitar furos de ventilação
ventilation_hole_diameter = 3.0; // Diâmetro dos furos (mm)
ventilation_spacing = 8.0;       // Espaçamento entre furos (mm)
fan_mount = false;               // Montagem para ventilador 40x40mm
heat_sink_mount = false;         // Suporte para dissipador de calor

// Acessórios e integrações
cable_grommets = true;     // Passa-cabos
antenna_external = false;  // Suporte para antena externa
display_cutout = true;     // Furo para display
button_access = true;      // Acesso a botões
sensor_holes = true;       // Furos para sensores
battery_compartment = false; // Compartimento para bateria

// LED e indicadores
led_windows = true;        // Janelas para LEDs
led_count = 2;            // Número de LEDs visíveis
led_size = 2.0;           // Diâmetro das janelas LED (mm)

// Configurações de impressão
layer_height = 0.2;        // Altura de camada preferencial
infill_percentage = 30;    // Porcentagem de infill
print_orientation = "upright"; // "flat", "upright", "angled"

// Montagem e instalação
wall_mount = false;        // Suporte para montagem em parede
desk_stand = true;         // Suporte para mesa
rubber_feet = true;        // Pés de borracha
magnet_mount = false;      // Imã para fixação metálica

// ==================== CÁLCULOS AUTOMÁTICOS ====================
// Não modifique abaixo desta linha - cálculos automáticos

// Dimensões externas da caixa
external_width = device_width + 2 * wall_thickness + 2 * clearance;
external_length = device_length + 2 * wall_thickness + 2 * clearance;
external_height = device_height + base_thickness + lid_gap;

// Posições dos elementos
base_center_z = -external_height/2 + base_thickness/2;
device_center_z = base_center_z + base_thickness/2 + device_height/2;
lid_center_z = external_height/2 - lid_gap/2;

// ==================== MÓDULOS DE CONSTRUÇÃO ====================

module base_box() {
    // Base principal da caixa
    difference() {
        // Caixa externa sólida
        cube([external_width, external_length, external_height]);
        
        // Cavidade interna para o dispositivo
        translate([wall_thickness/2, wall_thickness/2, base_thickness]) {
            cube([
                device_width + clearance,
                device_length + clearance, 
                device_height + lid_gap
            ]);
        }
        
        // Furo para Display (se habilitado)
        if (display_cutout) {
            translate([external_width/2, wall_thickness/2 + 5, device_center_z]) {
                cube([20, 3, device_height/2]);
            }
        }
        
        // Furos para botões (se habilitado)
        if (button_access) {
            button_positions = [
                [5, external_length - 10, device_center_z + device_height/4],
                [external_width - 5, external_length - 10, device_center_z + device_height/4]
            ];
            
            for (pos = button_positions) {
                translate(pos) {
                    cylinder(h=base_thickness + 5, d=3.0);
                }
            }
        }
        
        // Janelas para LEDs (se habilitado)
        if (led_windows) {
            led_positions = [];
            for (i = [0:led_count-1]) {
                x = (i == 0) ? external_width/2 - 5 : external_width/2 + 5;
                led_positions = concat(led_positions, [[x, external_length - 8, device_center_z]]);
            }
            
            for (pos = led_positions) {
                translate(pos) {
                    cylinder(h=base_thickness + 3, d=led_size);
                }
            }
        }
        
        // Furos para sensores (se habilitado)
        if (sensor_holes) {
            sensor_positions = [
                [wall_thickness + 3, wall_thickness + 3, device_center_z],
                [external_width - wall_thickness - 3, wall_thickness + 3, device_center_z]
            ];
            
            for (pos = sensor_positions) {
                translate(pos) {
                    cylinder(h=base_thickness + 3, d=2.5);
                }
            }
        }
        
        // Furos de ventilação (se habilitado)
        if (ventilation_enabled) {
            ventilation_grid();
        }
        
        // Montagem para ventilador (se habilitado)
        if (fan_mount) {
            fan_mount_holes();
        }
        
        // Furos para parafusos (se habilitado)
        if (screw_holes) {
            screw_holes_positions();
        }
    }
}

module ventilation_grid() {
    // Grade de ventilação na base
    start_x = wall_thickness + 5;
    end_x = external_width - wall_thickness - 5;
    start_y = wall_thickness + 5;
    end_y = external_length - wall_thickness - 5;
    
    for (x = [start_x : ventilation_spacing : end_x]) {
        for (y = [start_y : ventilation_spacing : end_y]) {
            translate([x, y, 0]) {
                cylinder(h=base_thickness + 2, d=ventilation_hole_diameter);
            }
        }
    }
}

module fan_mount_holes() {
    // Furos para montagem de ventilador 40x40mm
    fan_size = 40;
    fan_offset = fan_size/2 - 5;
    
    fan_hole_positions = [
        [-fan_offset, -fan_offset, 0],
        [fan_offset, -fan_offset, 0],
        [-fan_offset, fan_offset, 0],
        [fan_offset, fan_offset, 0]
    ];
    
    for (pos = fan_hole_positions) {
        translate([external_width/2 + pos[0], external_length/2 + pos[1], 0]) {
            cylinder(h=base_thickness + 3, d=3.0);
        }
    }
}

module screw_holes_positions() {
    // Posições dos furos para parafusos M3
    screw_positions = [
        [wall_thickness/2, wall_thickness/2, 0],
        [external_width - wall_thickness/2, wall_thickness/2, 0],
        [wall_thickness/2, external_length - wall_thickness/2, 0],
        [external_width - wall_thickness/2, external_length - wall_thickness/2, 0]
    ];
    
    for (pos = screw_positions) {
        translate(pos) {
            cylinder(h=base_thickness + 2, d=3.2); // M3 hole
        }
    }
}

module snap_fits() {
    // Snap fits para tampa (se tipo = snap)
    if (lid_type == "snap") {
        snap_positions = [
            [wall_thickness/2, wall_thickness/2, base_thickness],
            [external_width - wall_thickness/2, wall_thickness/2, base_thickness],
            [wall_thickness/2, external_length - wall_thickness/2, base_thickness],
            [external_width - wall_thickness/2, external_length - wall_thickness/2, 0]
        ];
        
        for (pos = snap_positions) {
            translate([pos[0], pos[1], external_height/2 - 1]) {
                // Snap fit proeminência
                difference() {
                    cylinder(h=2, d=5.0);
                    cylinder(h=2, d=4.0 + snap_tolerance);
                }
            }
        }
    }
}

module cable_grommets() {
    // Passa-cabos nas laterais
    if (cable_grommets) {
        grommet_positions = [
            [0, external_length/2, base_thickness + 5],
            [external_width, external_length/2, base_thickness + 5]
        ];
        
        for (pos = grommet_positions) {
            translate(pos) {
                cylinder(h=8, d=6.0); // Grommet hole
            }
        }
    }
}

module lid() {
    // Tampa da caixa
    if (lid_type != "none") {
        translate([0, 0, lid_center_z]) {
            difference() {
                // Tampa sólida
                cube([external_width, external_length, lid_gap]);
                
                // Recuo interno para snap fits
                if (lid_type == "snap") {
                    snap_rec_positions = [
                        [wall_thickness/2, wall_thickness/2, -lid_gap/2],
                        [external_width - wall_thickness/2, wall_thickness/2, -lid_gap/2],
                        [wall_thickness/2, external_length - wall_thickness/2, -lid_gap/2],
                        [external_width - wall_thickness/2, external_length - wall_thickness/2, -lid_gap/2]
                    ];
                    
                    for (pos = snap_rec_positions) {
                        translate(pos) {
                            cylinder(h=lid_gap/2, d=6.0);
                        }
                    }
                }
                
                // Furos para ventilação na tampa (se habilitado)
                if (ventilation_enabled) {
                    ventilation_grid_top();
                }
            }
        }
    }
}

module ventilation_grid_top() {
    // Grade de ventilação na tampa
    start_x = wall_thickness + 5;
    end_x = external_width - wall_thickness - 5;
    start_y = wall_thickness + 5;
    end_y = external_length - wall_thickness - 5;
    
    for (x = [start_x : ventilation_spacing : end_x]) {
        for (y = [start_y : ventilation_spacing : end_y]) {
            translate([x, y, lid_gap/2 + 0.1]) {
                cylinder(h=lid_gap/2, d=ventilation_hole_diameter);
            }
        }
    }
}

module wall_mount_supports() {
    // Suportes para montagem em parede
    if (wall_mount) {
        mount_positions = [
            [external_width/2, 0, external_height/2],
            [external_width/2, external_length, external_height/2]
        ];
        
        for (pos = mount_positions) {
            translate(pos) {
                cube([15, 5, 20]); // Support bracket
                
                // Furo para parafuso na parede
                translate([7.5, 2.5, 10]) {
                    cylinder(h=22, d=6.0);
                }
            }
        }
    }
}

module desk_stand() {
    // Suporte para mesa
    if (desk_stand) {
        // Base do suporte
        translate([external_width/2, external_length + 10, base_thickness]) {
            cube([20, 30, base_thickness]);
            
            // Suporte inclinado
            translate([0, 5, 0]) {
                cube([20, 5, 20]);
                translate([10, 0, 20]) {
                    rotate([0, -20, 0]) {
                        cube([20, 5, 25]);
                    }
                }
            }
        }
    }
}

module rubber_feet() {
    // Pés de borracha
    if (rubber_feet) {
        foot_positions = [
            [wall_thickness, wall_thickness, -external_height/2 - 2],
            [external_width - wall_thickness, wall_thickness, -external_height/2 - 2],
            [wall_thickness, external_length - wall_thickness, -external_height/2 - 2],
            [external_width - wall_thickness, external_length - wall_thickness, -external_height/2 - 2]
        ];
        
        for (pos = foot_positions) {
            translate(pos) {
                cylinder(h=4, d=8.0);
            }
        }
    }
}

// ==================== ASSEMBLY FINAL ====================

// Base da caixa
base_box();

// Snap fits para tampa
snap_fits();

// Tampa
lid();

// Passa-cabos
cable_grommets();

// Suporte de mesa
desk_stand();

// Pés de borracha
rubber_feet();

// Suporte para parede
wall_mount_supports();

// ==================== INFORMAÇÕES DE CONFIGURAÇÃO ====================

module print_info() {
    translate([0, -external_length/2 - 20, 0]) {
        linear_extrude(height=0.5) {
            text("3dPot Universal Case", size=4, halign="center");
            translate([0, -6, 0]) {
                text(str(device_width) + "x" + str(device_length) + "x" + str(device_height) + "mm", size=3, halign="center");
            }
            translate([0, -12, 0]) {
                text("Lid: " + lid_type, size=2.5, halign="center");
            }
            translate([0, -18, 0]) {
                text("Ventilation: " + str(ventilation_enabled), size=2.5, halign="center");
            }
        }
    }
}

print_info();

// ==================== PARÂMETROS DE IMPRESSÃO ====================

/*
INSTRUÇÕES DE IMPRESSÃO 3D:

1. CONFIGURAÇÕES RECOMENDADAS:
   - Material: PLA, PETG, ABS
   - Temperatura: PLA (200-220°C), PETG (220-250°C)
   - Altura da camada: 0.15-0.25mm (usar valor definido em layer_height)
   - Velocidade: 50-80mm/s
   - Infill: Usar valor definido em infill_percentage

2. ORIENTAÇÃO DE IMPRESSÃO:
   - Para melhor qualidade: base para baixo
   - Para menos suporte: lateralmente
   - Para velocidade: de lado

3. SUPORTE:
   - Não necessário para este design
   - Use suporte apenas para overhangs > 45°

4. PÓS-PROCESSAMENTO:
   - Lixar levemente as superfícies
   - Testar snap fits
   - Limpar furos com broca

5. CONFIGURAÇÕES DISPONÍVEIS:
   - Modifique as variáveis no topo do arquivo
   - Re-render para ver alterações
   - Salve versões com nomes diferentes

6. COMPATIBILIDADE:
   - ESP32 DevKit
   - Arduino Uno/Nano
   - Raspberry Pi Zero/4
   - Dispositivos customizados
*/