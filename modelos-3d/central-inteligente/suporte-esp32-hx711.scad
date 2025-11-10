// Suporte Modular para ESP32 + Monitor de Filamento
// Inclui furação para sensor HX711 e ventilação

// Dimensões do ESP32 DevKit
esp32_largura = 30;    // 3.0cm
esp32_profundidade = 20; // 2.0cm
esp32_altura = 4;      // 0.4cm

// Dimensões do sensor HX711
hx711_largura = 15;    // 1.5cm
hx711_profundidade = 25; // 2.5cm
hx711_altura = 2;      // 0.2cm

// Dimensões do suporte
suporte_largura = 40;
suporte_profundidade = 35;
suporte_altura = 5;

// Furações
furo_diametro = 3.5;
furo_espacamento = 20;
margin = 10;

// Posicionamento
esp32_offset_x = (suporte_largura - esp32_largura) / 2;
esp32_offset_y = 5;

hx711_offset_x = (suporte_largura - hx711_largura) / 2;
hx711_offset_y = suporte_profundidade - hx711_profundidade - 5;

// Criar base do suporte
difference() {
    // Base principal
    cube([suporte_largura, suporte_profundidade, suporte_altura]);
    
    // Furo para LED de status do ESP32
    translate([suporte_largura/2, 2, -1]) {
        cylinder(h = suporte_altura + 2, d = 3, $fn = 15);
    }
    
    // Furos de montagem
    for (x = [margin, suporte_largura - margin]) {
        for (y = [margin, suporte_profundidade - margin]) {
            translate([x, y, -1]) {
                cylinder(h = suporte_altura + 2, d = furo_diametro, $fn = 20);
            }
        }
    }
}

// Rebaixo para ESP32
translate([esp32_offset_x, esp32_offset_y, 0]) {
    difference() {
        cube([esp32_largura, esp32_profundidade, 2]);
        cube([esp32_largura - 2, esp32_profundidade - 2, 3]);
    }
    
    // Furos dos pinos do ESP32
    // Linha superior de pinos
    for (i = [2:3:esp32_largura-2]) {
        translate([i, 1, -1]) {
            cylinder(h = 3, d = 1, $fn = 10);
        }
    }
    
    // Linha inferior de pinos
    for (i = [2:3:esp32_largura-2]) {
        translate([i, esp32_profundidade - 1, -1]) {
            cylinder(h = 3, d = 1, $fn = 10);
        }
    }
    
    // Furos dos LEDs do ESP32
    translate([esp32_largura - 3, esp32_profundidade/2, -1]) {
        cylinder(h = 3, d = 2, $fn = 15);
    }
}

// Rebaixo para sensor HX711
translate([hx711_offset_x, hx711_offset_y, 0]) {
    difference() {
        cube([hx711_largura, hx711_profundidade, 2]);
        cube([hx711_largura - 2, hx711_profundidade - 2, 3]);
    }
    
    // Furos para os pinos HX711
    // Pino VCC, GND, SCK, DT (superior)
    for (i = [2, 5, 8, 11]) {
        translate([i, 1, -1]) {
            cylinder(h = 3, d = 1, $fn = 10);
        }
    }
    
    // Pinos de sensor (inferior)
    for (i = [2, 5, 8, 11]) {
        translate([i, hx711_profundidade - 1, -1]) {
            cylinder(h = 3, d = 1, $fn = 10);
        }
    }
}

// Guia de cabos entre ESP32 e HX711
translate([suporte_largura/2, 22, 0]) {
    // Ranhura para passagem de cabos
    cube([15, 8, 2]);
    
    // Furo de saída de cabos
    translate([7.5, -1, -1]) {
        cylinder(h = 3, d = 6, $fn = 20);
    }
}

// Suporte para balança (HX711)
// Base da balança
translate([hx711_offset_x + 2, hx711_offset_y - 15, 0]) {
    difference() {
        cube([hx711_largura - 4, 15, 2]);
        cube([hx711_largura - 8, 15, 3]);
    }
    
    // Furos para parafusos da balança
    for (x = [3, hx711_largura - 8]) {
        for (y = [3, 12]) {
            translate([x, y, -1]) {
                cylinder(h = 3, d = 2, $fn = 10);
            }
        }
    }
}

// Abas de ventilação
for (i = [5:10:suporte_largura-5]) {
    translate([i, suporte_profundidade/2 - 1, 0]) {
        cube([8, 2, suporte_altura]);
    }
}

// Label identificativo
color("red") {
    translate([suporte_largura/2 - 12, 2, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("ESP32", size = 4, font = "Arial:style=Bold");
        }
    }
    
    translate([hx711_offset_x + 2, hx711_offset_y - 18, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("H X711", size = 3, font = "Arial:style=Bold");
        }
    }
}

// Pés de borracha (inserts)
for (x = [margin, suporte_largura - margin]) {
    for (y = [margin, suporte_profundidade - margin]) {
        translate([x, y, -1]) {
            // Insert roscado M3
            cylinder(h = 4, d = 4, $fn = 20);
            translate([0, 0, 1]) {
                cylinder(h = 3, d = 2.5, $fn = 20);
            }
        }
    }
}

// Ventilação adicional
for (i = [8:8:suporte_largura-8]) {
    translate([i, suporte_profundidade - 3, -1]) {
        cylinder(h = suporte_altura + 2, d = 2, $fn = 10);
    }
}

// Guia de impressão
echo("=== Suporte ESP32 + HX711 ===");
echo("Dimensões:", suporte_largura, "x", suporte_profundidade, "x", suporte_altura);
echo("Área de impressão: 45x40mm");
echo("Suporte: Sim (pinos e inserts)");
echo("Altura de camada: 0.15mm");
echo("Infill: 30%");
echo("Material recomendado: PETG (melhor resistência térmica)");