// Suporte Universal para Fonte e Conectores
// Sistema modular para alimentação e distribuição de energia

// Dimensões da fonte 12V/5V (60W típica)
fonte_largura = 80;        // 8.0cm
fonte_profundidade = 50;   // 5.0cm  
fonte_altura = 25;         // 2.5cm

// Dimensões do suporte
suporte_largura = 100;
suporte_profundidade = 60;
suporte_altura = 8;

// Layout dos componentes
fonte_offset_x = 5;
fonte_offset_y = 5;

conectores_x = fonte_offset_x + fonte_largura + 5;
conectores_y = 5;

// Painel de conectores
conector_diametro = 8;
conector_espacamento = 15;
num_conectores = 6;

// Distribuidor de energia (módulo ESP32)
distribuidor_largura = 25;
distribuidor_profundidade = 20;
distribuidor_offset_x = 5;
distribuidor_offset_y = fonte_offset_y + fonte_profundidade + 10;

// Furações
furo_diametro = 3.5;
margin = 15;

// Conectores JST-PH (2mm pitch)
// ESP32
esp32_conectores = [
    [conectores_x, conectores_y, "ESP32"],
    [conectores_x, conectores_y + conector_espacamento, "12V"],
    [conectores_x, conectores_y + 2*conector_espacamento, "5V"],
    [conectores_x, conectores_y + 3*conector_espacamento, "GND"]
];

// Arduino
arduino_conectores = [
    [conectores_x + 25, conectores_y, "Arduino"],
    [conectores_x + 25, conectores_y + conector_espacamento, "12V"],
    [conectores_x + 25, conectores_y + 2*conector_espacamento, "5V"],
    [conectores_x + 25, conectores_y + 3*conector_espacamento, "GND"]
];

// Raspberry Pi
rpi_conectores = [
    [conectores_x + 50, conectores_y, "RPi"],
    [conectores_x + 50, conectores_y + conector_espacamento, "5V"],
    [conectores_x + 50, conectores_y + 2*conector_espacamento, "5V"],
    [conectores_x + 50, conectores_y + 3*conector_espacamento, "GND"]
];

// Motores (12V)
motor_conectores = [
    [conectores_x, conectores_y + 5*conector_espacamento, "STEPPER"],
    [conectores_x, conectores_y + 6*conector_espacamento, "STEPPER"],
    [conectores_x, conectores_y + 7*conector_espacamento, "STEPPER"]
];

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
    
    // Rebaixo para fonte
    translate([fonte_offset_x, fonte_offset_y, 0]) {
        cube([fonte_largura, fonte_profundidade, 3]);
        
        // Furos para montagem da fonte
        for (x = [5, fonte_largura - 5]) {
            for (y = [5, fonte_profundidade - 5]) {
                translate([x, y, -1]) {
                    cylinder(h = 4, d = 2, $fn = 15);
                }
            }
        }
        
        // Ventilação da fonte
        for (x = [10:15:fonte_largura-10]) {
            for (y = [10:10:fonte_profundidade-10]) {
                translate([x, y, -1]) {
                    cylinder(h = 4, d = 5, $fn = 15);
                }
            }
        }
    }
    
    // Furos dos conectores
    for (grupo_conectores in [esp32_conectores, arduino_conectores, rpi_conectores, motor_conectores]) {
        for (conector = grupo_conectores) {
            translate([conector[0], conector[1], -1]) {
                cylinder(h = suporte_altura + 2, d = conector_diametro, $fn = 20);
            }
        }
    }
}

// Suporte para distribuidor de energia
translate([distribuidor_offset_x, distribuidor_offset_y, 0]) {
    difference() {
        cube([distribuidor_largura, distribuidor_profundidade, 2]);
        cube([distribuidor_largura - 2, distribuidor_profundidade - 2, 3]);
    }
    
    // Furos para LEDs indicadores
    for (i = [0:3]) {
        translate([3 + i*6, distribuidor_profundidade - 3, -1]) {
            cylinder(h = 3, d = 2, $fn = 15);
        }
    }
    
    // LED verde (12V OK)
    color("green") {
        translate([3, distribuidor_profundidade - 2, 0]) {
            cylinder(h = 1, d = 3, $fn = 15);
        }
    }
    
    // LED azul (5V OK)  
    color("blue") {
        translate([9, distribuidor_profundidade - 2, 0]) {
            cylinder(h = 1, d = 3, $fn = 15);
        }
    }
    
    // LED vermelho (erro)
    color("red") {
        translate([15, distribuidor_profundidade - 2, 0]) {
            cylinder(h = 1, d = 3, $fn = 15);
        }
    }
    
    // LED amarelo (sobrecarga)
    color("yellow") {
        translate([21, distribuidor_profundidade - 2, 0]) {
            cylinder(h = 1, d = 3, $fn = 15);
        }
    }
}

// Tampa com ventilação
translate([fonte_offset_x, fonte_offset_y, fonte_altura + 3]) {
    difference() {
        cube([fonte_largura, fonte_profundidade, 2]);
        
        // Furos de ventilação
        for (x = [5:15:fonte_largura-5]) {
            for (y = [5:15:fonte_profundidade-5]) {
                translate([x, y, -1]) {
                    cylinder(h = 4, d = 8, $fn = 20);
                }
            }
        }
    }
    
    // Grade de proteção
    for (i = [0:2:fonte_largura-5]) {
        for (j = [0:2:fonte_profundidade-5]) {
            translate([i, j, 0]) {
                cube([4, 4, 2]);
            }
        }
    }
}

// Conectores etiquetados
module conector_etiquetado(pos, tipo) {
    // Base do conector
    color("black") {
        translate([pos[0], pos[1], suporte_altura - 1]) {
            cylinder(h = 2, d = conector_diametro, $fn = 20);
        }
    }
    
    // Cor do conector baseada no tipo
    if (pos[2] == "12V") {
        color("red") {
            translate([pos[0], pos[1], suporte_altura - 2]) {
                cylinder(h = 1, d = conector_diametro - 2, $fn = 20);
            }
        }
    } else if (pos[2] == "5V") {
        color("blue") {
            translate([pos[0], pos[1], suporte_altura - 2]) {
                cylinder(h = 1, d = conector_diametro - 2, $fn = 20);
            }
        }
    } else if (pos[2] == "GND") {
        color("black") {
            translate([pos[0], pos[1], suporte_altura - 2]) {
                cylinder(h = 1, d = conector_diametro - 2, $fn = 20);
            }
        }
    } else {
        color("white") {
            translate([pos[0], pos[1], suporte_altura - 2]) {
                cylinder(h = 1, d = conector_diametro - 2, $fn = 20);
            }
        }
    }
    
    // Text label
    color("black") {
        translate([pos[0] - 8, pos[1] - 3, suporte_altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text(tipo, size = 2, font = "Arial:style=Bold");
            }
        }
    }
}

// Adicionar todos os conectores
for (grupo in [esp32_conectores, arduino_conectores, rpi_conectores, motor_conectores]) {
    for (conector in grupo) {
        conector_etiquetado(conector, conector[2]);
    }
}

// Painel de controle de energia
translate([conectores_x + 75, conectores_y + 5, 0]) {
    // Base do painel
    difference() {
        cube([20, 25, 3]);
        cube([20, 25, 4]);
    }
    
    // LED de status geral
    translate([10, 2, -1]) {
        cylinder(h = 4, d = 4, $fn = 15);
    }
    
    color("green") {
        translate([10, 2, 0]) {
            cylinder(h = 1, d = 6, $fn = 15);
        }
    }
    
    // Chave liga/desliga
    translate([10, 10, 0]) {
        // Base da chave
        color("black") {
            cylinder(h = 1, d = 8, $fn = 20);
        }
        
        // Chave ON
        color("green") {
            translate([0, 0, 0.5]) {
                cylinder(h = 3, d = 2, $fn = 10);
            }
        }
    }
    
    // Botão de reset
    translate([10, 18, 0]) {
        color("red") {
            cylinder(h = 2, d = 6, $fn = 20);
        }
    }
}

// Indicador de potência
translate([fonte_offset_x + 10, fonte_offset_y + fonte_profundidade + 5, 0]) {
    color("red") {
        linear_extrude(height = 0.3) {
            text("POWER", size = 4, font = "Arial:style=Bold");
        }
    }
    
    translate([fonte_offset_x + 10, fonte_offset_y + fonte_profundidade + 12, 0]) {
        color("red") {
            linear_extrude(height = 0.3) {
                text("60W MAX", size = 3);
            }
        }
    }
}

// Canal de cables
translate([conectores_x - 5, conectores_y + 8*conector_espacamento, 0]) {
    cube([conectores_x + 80, 8, 4]);
    
    // Furos para passagem de cables
    for (i = [5:10:conectores_x + 75]) {
        translate([i, 4, -1]) {
            cylinder(h = 6, d = 4, $fn = 15);
        }
    }
}

// Proteção contra sobrecarga
for (i = [0:3]) {
    translate([fonte_offset_x + 60 + i*8, fonte_offset_y + 5, 0]) {
        // Fusível térmico
        color("yellow") {
            cylinder(h = 1, d = 6, $fn = 15);
        }
    }
}

// Pés anti-derrapante
for (x = [margin, suporte_largura - margin]) {
    for (y = [margin, suporte_profundidade - margin]) {
        translate([x, y, -2]) {
            color("black") {
                cylinder(h = 4, d = 8, $fn = 20);
            }
        }
    }
}

// Ventilação forçada (fans)
for (x = [20, 80]) {
    translate([x, suporte_profundidade - 10, 0]) {
        difference() {
            cylinder(h = 2, d = 15, $fn = 30);
            cylinder(h = 3, d = 12, $fn = 30);
        }
        
        // Pás do ventilador
        for (i = [0:3]) {
            angle = i * 90;
            fan_x = 6 * cos(angle);
            fan_y = 6 * sin(angle);
            translate([fan_x, fan_y, 0]) {
                color("gray") {
                    cube([12, 2, 2]);
                }
            }
        }
    }
}

// Label principal
color("red") {
    translate([suporte_largura/2 - 15, suporte_profundidade/2, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("POWER", size = 6, font = "Arial:style=Bold");
        }
    }
    
    translate([suporte_largura/2 - 20, suporte_profundidade/2 + 8, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("MODULE", size = 4);
        }
    }
}

// Guia de impressão
echo("=== Suporte Fonte de Alimentação ===");
echo("Dimensões:", suporte_largura, "x", suporte_profundidade, "x", (suporte_altura + fonte_altura + 3));
echo("Área de impressão: 105x65mm");
echo("Suporte: Sim (múltiplas áreas)");
echo("Altura de camada: 0.2mm");
echo("Infill: 45%");
echo("Velocidade: 50mm/s");
echo("Material: ABS (resistência térmica)");
echo("Observações: Printar em 2 partes se necessário");