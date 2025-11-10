// Suporte para Arduino Uno/Nano + Esteirão de Controle
// Inclui furação para LED de status, botão de emergência e conectores

// Dimensões do Arduino Uno
arduino_largura = 35;      // 3.5cm
arduino_profundidade = 25; // 2.5cm
arduino_altura = 6;        // 0.6cm (considerando componentes)

// Dimensões do suporte
suporte_largura = 50;
suporte_profundidade = 35;
suporte_altura = 8;

// Layout dos componentes no Arduino
pino_spacing = 2.5;
num_pinos_lado = 8;
conector_usb_largura = 9;
conector_usb_profundidade = 8;

// Furações
furo_diametro = 3.5;
furo_espacamento = 25;
margin = 8;

// Posicionamento
arduino_offset_x = (suporte_largura - arduino_largura) / 2;
arduino_offset_y = 8;

// Área para LED de status
led_area_largura = 8;
led_area_profundidade = 6;
led_pos_x = arduino_offset_x + arduino_largura + 5;
led_pos_y = 12;

// Área para botão de emergência
botao_diametro = 12;
botao_pos_x = arduino_offset_x + arduino_largura + 5;
botao_pos_y = suporte_profundidade - 15;

// Conectores de controle para motores
conector_diametro = 8;
conectores_y = [20, 25, 30];
conector_pos_x = arduino_offset_x - 8;

// Criar base do suporte
difference() {
    // Base principal
    cube([suporte_largura, suporte_profundidade, suporte_altura]);
    
    // Furos de montagem
    for (x = [margin, suporte_largura - margin]) {
        for (y = [margin, suporte_profundidade - margin]) {
            translate([x, y, -1]) {
                cylinder(h = suporte_altura + 2, d = furo_diametro, $fn = 20);
            }
        }
    }
    
    // Furo para LED de status
    translate([led_pos_x, led_pos_y, -1]) {
        cylinder(h = suporte_altura + 2, d = led_area_largura, $fn = 20);
    }
    
    // Furo para botão de emergência
    translate([botao_pos_x, botao_pos_y, -1]) {
        cylinder(h = suporte_altura + 2, d = botao_diametro, $fn = 20);
    }
    
    // Furos para conectores de motores
    for (y = conectores_y) {
        translate([conector_pos_x, y, -1]) {
            cylinder(h = suporte_altura + 2, d = conector_diametro, $fn = 20);
        }
    }
}

// Rebaixo para Arduino
translate([arduino_offset_x, arduino_offset_y, 0]) {
    difference() {
        cube([arduino_largura, arduino_profundidade, 3]);
        cube([arduino_largura - 2, arduino_profundidade - 2, 4]);
    }
    
    // Furos para pinos digitais (lado direito)
    for (i = [1:num_pinos_lado]) {
        x_pos = arduino_largura - 2;
        y_pos = 2 + (i - 1) * pino_spacing;
        translate([x_pos, y_pos, -1]) {
            cylinder(h = 4, d = 1, $fn = 10);
        }
    }
    
    // Furos para pinos analógicos (lado esquerdo)
    for (i = [1:num_pinos_lado]) {
        x_pos = 2;
        y_pos = 2 + (i - 1) * pino_spacing;
        translate([x_pos, y_pos, -1]) {
            cylinder(h = 4, d = 1, $fn = 10);
        }
    }
    
    // Rebaixo para conector USB
    translate([arduino_largura - conector_usb_largura - 2, 1, 0]) {
        cube([conector_usb_largura, conector_usb_profundidade, 4]);
    }
    
    // Furos de ventilação (através do Arduino)
    for (i = [5:5:arduino_largura-5]) {
        for (j = [8:5:arduino_profundidade-8]) {
            translate([i, j, -1]) {
                cylinder(h = 4, d = 2, $fn = 10);
            }
        }
    }
}

// Suporte para botão de emergência
translate([botao_pos_x, botao_pos_y, suporte_altura - 2]) {
    // Anel de proteção
    difference() {
        cylinder(h = 2, d = botao_diametro + 4, $fn = 20);
        cylinder(h = 3, d = botao_diametro, $fn = 20);
    }
    
    // Botão vermelho
    color("red") {
        cylinder(h = 1, d = botao_diametro, $fn = 20);
    }
}

// Suporte para LED de status
translate([led_pos_x, led_pos_y, suporte_altura - 2]) {
    // Base do LED
    color("black") {
        cylinder(h = 1, d = 6, $fn = 15);
    }
    
    // LED verde (sucesso)
    color("green") {
        translate([0, 0, 0.5]) {
            cylinder(h = 1, d = 4, $fn = 15);
        }
    }
    
    // LED vermelho (erro)
    color("red") {
        translate([3, 0, 0.5]) {
            cylinder(h = 1, d = 4, $fn = 15);
        }
    }
    
    // LED amarelo (em operação)
    color("yellow") {
        translate([0, 3, 0.5]) {
            cylinder(h = 1, d = 4, $fn = 15);
        }
    }
}

// Conectores para controle de motores
for (y = conectores_y) {
    // Cabo STEP (Motor de passo)
    translate([conector_pos_x, y, suporte_altura - 1]) {
        color("blue") {
            cylinder(h = 2, d = conector_diametro, $fn = 20);
        }
    }
    
    // Cabo DIR
    translate([conector_pos_x - 12, y, suporte_altura - 1]) {
        color("green") {
            cylinder(h = 2, d = conector_diametro, $fn = 20);
        }
    }
    
    // Cabo ENABLE
    translate([conector_pos_x - 24, y, suporte_altura - 1]) {
        color("orange") {
            cylinder(h = 2, d = conector_diametro, $fn = 20);
        }
    }
}

// Label identificativo
color("blue") {
    translate([suporte_largura/2 - 10, 2, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("Arduino", size = 4, font = "Arial:style=Bold");
        }
    }
    
    translate([conector_pos_x - 8, conectores_y[1] - 3, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("MOTOR", size = 3, font = "Arial:style=Bold");
        }
    }
}

// Canal para organização de cabos
translate([0, suporte_profundidade/2, 0]) {
    // Canal principal de cabos
    cube([suporte_largura, 4, 3]);
    
    // Círculos para passagem de cabos individuais
    for (i = [10:10:suporte_largura-10]) {
        translate([i, 2, -1]) {
            cylinder(h = 5, d = 3, $fn = 15);
        }
    }
}

// Pés de borracha
for (x = [margin, suporte_largura - margin]) {
    for (y = [margin, suporte_profundidade - margin]) {
        translate([x, y, -1]) {
            // Base do pé
            cylinder(h = 2, d = 6, $fn = 20);
            translate([0, 0, 1]) {
                // Insert roscado
                cylinder(h = 3, d = 3, $fn = 20);
            }
        }
    }
}

// Ventilação
for (i = [15:10:suporte_largura-15]) {
    translate([i, 30, -1]) {
        cylinder(h = suporte_altura + 2, d = 3, $fn = 15);
    }
}

// Guia de impressão
echo("=== Suporte Arduino + Controle Esteirão ===");
echo("Dimensões:", suporte_largura, "x", suporte_profundidade, "x", suporte_altura);
echo("Área de impressão: 55x40mm");
echo("Suporte: Sim (pinos e LED)");
echo("Altura de camada: 0.2mm");
echo("Infill: 40%");
echo("Velocidade: 45mm/s");
echo("Material: ABS ou PETG (melhor tolerância térmica)");