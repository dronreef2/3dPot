// Chassi Principal da Central de Controle Inteligente 3dPot
// Suporte base modular para Arduino, ESP32, Raspberry Pi e equipamentos

// Dimensões principais
chassi_largura = 300;  // 30cm
chassi_profundidade = 200;  // 20cm
chassi_altura = 15;  // 1.5cm
parede_altura = 20;  // 2cm

// Espessuras
parede_espessura = 3;
base_espessura = 5;

// Posicionamento dos furos
furo_diametro = 3.5;
furo_profundidade = 8;
margin = 15;

// Posições dos furos (canto a canto)
furos = [
    [margin, margin, 0],
    [chassi_largura - margin, margin, 0],
    [margin, chassi_profundidade - margin, 0],
    [chassi_largura - margin, chassi_profundidade - margin, 0],
    [chassi_largura/2, margin, 0],
    [chassi_largura/2, chassi_profundidade - margin, 0],
    [margin, chassi_profundidade/2, 0],
    [chassi_largura - margin, chassi_profundidade/2, 0]
];

// Posições dos módulos eletrônicos
// ESP32: canto inferior esquerdo
esp32_pos = [20, 20, base_espessura];
esp32_size = [35, 25, 3];

// Arduino: canto inferior direito
arduino_pos = [chassi_largura - 55, 20, base_espessura];
arduino_size = [35, 25, 3];

// Raspberry Pi: centro
rpi_pos = [chassi_largura/2 - 25, chassi_profundidade/2 - 20, base_espessura];
rpi_size = [50, 40, 3];

// Motor de passo (esteira): centro-esquerda
motor_pos = [80, chassi_profundidade - 30, base_espessura];
motor_size = [40, 40, 5];

// Furo para passage de cabos
cabo_diametro = 15;
cabo_pos = [chassi_largura/2, chassi_profundidade - margin, base_espessura/2];

// Criar base principal
difference() {
    // Base sólida
    cube([chassi_largura, chassi_profundidade, base_espessura]);
    
    // Furos de montagem
    for (furo = furos) {
        translate(furo) {
            cylinder(h = furo_profundidade, d = furo_diametro, $fn = 20);
        }
    }
    
    // Furo para cabos
    translate([cabo_pos[0], cabo_pos[1], -1]) {
        cylinder(h = base_espessura + 2, d = cabo_diametro, $fn = 30);
    }
}

// Criar paredes laterais
// Parede frontal
translate([0, chassi_profundidade - parede_espessura, base_espessura]) {
    difference() {
        cube([chassi_largura, parede_espessura, parede_altura]);
        
        // Furo para display (opcional)
        translate([chassi_largura/2 - 30, parede_espessura/2, 5]) {
            cube([60, 1, 40]);
        }
        
        // Ventilação
        for (i = [20:25:chassi_largura-20]) {
            translate([i, parede_espessura/2, 15]) {
                cylinder(h = 5, d = 8, $fn = 15);
            }
        }
    }
}

// Parede lateral esquerda
translate([0, 0, base_espessura]) {
    difference() {
        cube([parede_espessura, chassi_profundidade, parede_altura]);
        
        // Furos para ventoinha
        for (j = [30:25:chassi_profundidade-30]) {
            translate([parede_espessura/2, j, 15]) {
                cylinder(h = 5, d = 20, $fn = 20);
            }
        }
    }
}

// Parede lateral direita
translate([chassi_largura - parede_espessura, 0, base_espessura]) {
    difference() {
        cube([parede_espessura, chassi_profundidade, parede_altura]);
        
        // Furos para cabos grandes
        for (j = [40, 80, 120, 160]) {
            translate([parede_espessura/2, j, 15]) {
                cylinder(h = 5, d = 12, $fn = 20);
            }
        }
    }
}

// Indicações dos módulos (rebaixos)
module modulo_suporte(pos, size, label) {
    translate([pos[0], pos[1], pos[2]]) {
        // Rebaixo para o módulo
        difference() {
            cube([size[0] + 6, size[1] + 6, 2]);
            cube([size[0] + 2, size[1] + 2, 3]);
        }
        
        // Textos indicativos
        color("red") {
            translate([size[0]/2 - 5, size[1]/2, 2.1]) {
                linear_extrude(height = 0.3) {
                    text(label, size = 3, font = "Arial:style=Bold");
                }
            }
        }
    }
}

// Adicionar suportes dos módulos
modulo_suporte(esp32_pos, esp32_size, "ESP32");
modulo_suporte(arduino_pos, arduino_size, "Arduino");
modulo_suporte(rpi_pos, rpi_size, "RPi");
modulo_suporte(motor_pos, motor_size, "Motor");

// Suporte para fonte de alimentação
fonte_pos = [chassi_largura - 80, 30, base_espessura];
fonte_size = [60, 30, 3];
translate([fonte_pos[0], fonte_pos[1], fonte_pos[2]]) {
    difference() {
        cube([fonte_size[0], fonte_size[1], 2]);
        cube([fonte_size[0] - 4, fonte_size[1] - 4, 3]);
    }
    
    // Furos para ventilação da fonte
    for (i = [10:15:50]) {
        for (j = [5:10:25]) {
            translate([i, j, 0]) {
                cylinder(h = 1, d = 3, $fn = 10);
            }
        }
    }
}

// Adicionar textos informativos
color("blue") {
    // Título principal
    translate([chassi_largura/2 - 25, 10, base_espessura + 2.1]) {
        linear_extrude(height = 0.3) {
            text("3dPot Central", size = 5, font = "Arial:style=Bold");
        }
    }
    
    // Subtítulo
    translate([chassi_largura/2 - 20, 25, base_espessura + 2.1]) {
        linear_extrude(height = 0.3) {
            text("Controle Inteligente", size = 3);
        }
    }
}

// Guia de impressão
echo("=== Chassi Principal 3dPot ===");
echo("Dimensões:", chassi_largura, "x", chassi_profundidade, "x", (base_espessura + parede_altura));
echo("Área de impressão mínima: 310x210mm");
echo("Altura de camada recomendada: 0.2mm");
echo("Infill: 20% para economia, 50% para resistência");
echo("Suportes necessários: Não");
echo("Velocidade de impressão: 50mm/s");