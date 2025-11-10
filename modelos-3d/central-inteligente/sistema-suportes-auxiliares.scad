// Sistema de Suportes Auxiliares para Central 3dPot
// Inclui plataforma giratória, organizador de cabos e gabaritos

// ====================
// PLATAFORMA GIRATÓRIA PARA ESTAÇÃO QC
// ====================

platforma_diametro = 60;    // 6cm diâmetro
platforma_altura = 5;       // 0.5cm altura
eixo_diametro = 6;          // eixo central
anel_rolamento_diametro = 40; // anel com rolamentos
anel_rolamento_altura = 3;


// ====================
// ORGANIZADOR DE CABOS
// ====================

organizador_largura = 100;
organizador_profundidade = 30;
organizador_altura = 15;
furo_cabo_diametro = 6;
num_furos = 8;


// ====================
// GABARITOS DE MONTAGEM
// ====================

gabarito_largura = 50;
gabarito_profundidade = 50;
gabarito_altura = 3;

// Posições dos gabaritos
gabarito_esp32 = [0, 0, 0];
gabarito_arduino = [55, 0, 0];
gabarito_raspberry = [0, 55, 0];
gabarito_motor = [55, 55, 0];

// ====================
// CÓDIGO DE IMPRESSÃO
// ====================

module plataforma_giratoria() {
    echo("Gerando Plataforma Giratória QC...");
    
    // Base da plataforma
    difference() {
        cylinder(h = platforma_altura, d = platforma_diametro, $fn = 40);
        
        // Eixo central
        cylinder(h = platforma_altura + 2, d = eixo_diametro, $fn = 20);
        
        // Anel de rolamento
        cylinder(h = platforma_altura + 1, d = anel_rolamento_diametro, $fn = 30);
    }
    
    // Superfície anti-derrapante
    translate([0, 0, platforma_altura - 0.5]) {
        // Padrão de ranhuras
        for (i = [0:20:platforma_diametro-10]) {
            angle = i * 360 / platforma_diametro;
            x = (platforma_diametro/2 - 5) * cos(angle);
            y = (platforma_diametro/2 - 5) * sin(angle);
            translate([x, y, 0]) {
                cylinder(h = 1, d = 2, $fn = 10);
            }
        }
    }
    
    // Furos para fixação de amostras
    for (i = [0:5]) {
        angle = i * 72;  // 6 posições
        x = (platforma_diametro/2 - 8) * cos(angle);
        y = (platforma_diametro/2 - 8) * sin(angle);
        translate([x, y, -1]) {
            cylinder(h = platforma_altura + 2, d = 2, $fn = 10);
        }
    }
    
    // Label identificativo
    color("blue") {
        translate([-12, -2, platforma_altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text("QC", size = 8, font = "Arial:style=Bold");
            }
        }
    }
}

module organizador_cabos() {
    echo("Gerando Organizador de Cabos...");
    
    difference() {
        // Base do organizador
        cube([organizador_largura, organizador_profundidade, organizador_altura]);
        
        // Furos para passagem de cabos
        for (i = [0:num_furos-1]) {
            x = 10 + i * (organizador_largura - 20) / (num_furos - 1);
            translate([x, organizador_profundidade/2, -1]) {
                cylinder(h = organizador_altura + 2, d = furo_cabo_diametro, $fn = 15);
            }
        }
        
        // Furos de montagem
        for (x = [8, organizador_largura - 8]) {
            for (y = [8, organizador_profundidade - 8]) {
                translate([x, y, -1]) {
                    cylinder(h = organizador_altura + 2, d = 3.5, $fn = 20);
                }
            }
        }
    }
    
    // Separadores internos
    for (i = [0:num_furos-2]) {
        x = 15 + i * (organizador_largura - 30) / (num_furos - 2);
        translate([x, 0, organizador_altura - 2]) {
            cube([1, organizador_profundidade, 4]);
        }
    }
    
    // Área de encaixe para as Peças eletrônicas
    // ESP32
    translate([5, organizador_profundidade - 8, 0]) {
        color("white") {
            linear_extrude(height = 0.3) {
                text("ESP32", size = 2);
            }
        }
    }
    
    // Arduino
    translate([15, organizador_profundidade - 8, 0]) {
        color("white") {
            linear_extrude(height = 0.3) {
                text("Arduino", size = 2);
            }
        }
    }
    
    // Raspberry Pi
    translate([25, organizador_profundidade - 8, 0]) {
        color("white") {
            linear_extrude(height = 0.3) {
                text("RPi", size = 2);
            }
        }
    }
    
    // LED de status
    translate([organizador_largura - 5, 2, -1]) {
        color("green") {
            cylinder(h = organizador_altura + 2, d = 3, $fn = 15);
        }
    }
}

module gabarito_esp32() {
    echo("Gerando Gabarito ESP32...");
    
    difference() {
        // Base do gabarito
        cube([gabarito_largura, gabarito_profundidade, gabarito_altura]);
        
        // Contorno do ESP32
        translate([12, 10, 0]) {
            cube([26, 20, gabarito_altura + 1]);
            
            // Furos dos pinos
            for (x = [0:3:25]) {
                for (y = [0:3:19]) {
                    translate([x, y, -1]) {
                        cylinder(h = gabarito_altura + 2, d = 1, $fn = 8);
                    }
                }
            }
        }
        
        // Furos de montagem
        for (x = [8, gabarito_largura - 8]) {
            for (y = [8, gabarito_profundidade - 8]) {
                translate([x, y, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 3.5, $fn = 20);
                }
            }
        }
    }
    
    // Indicação de posição
    color("green") {
        translate([gabarito_largura/2 - 8, gabarito_profundidade - 5, gabarito_altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text("ESP32", size = 3, font = "Arial:style=Bold");
            }
        }
    }
}

module gabarito_arduino() {
    echo("Gerando Gabarito Arduino...");
    
    difference() {
        // Base do gabarito
        cube([gabarito_largura, gabarito_profundidade, gabarito_altura]);
        
        // Contorno do Arduino
        translate([10, 8, 0]) {
            cube([30, 22, gabarito_altura + 1]);
            
            // Furos dos pinos
            for (x = [0:3:27]) {
                for (y = [0:3:20]) {
                    translate([x, y, -1]) {
                        cylinder(h = gabarito_altura + 2, d = 1, $fn = 8);
                    }
                }
            }
        }
        
        // Furos de montagem
        for (x = [8, gabarito_largura - 8]) {
            for (y = [8, gabarito_profundidade - 8]) {
                translate([x, y, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 3.5, $fn = 20);
                }
            }
        }
    }
    
    // Indicação de posição
    color("blue") {
        translate([gabarito_largura/2 - 10, gabarito_profundidade - 5, gabarito_altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text("Arduino", size = 3, font = "Arial:style=Bold");
            }
        }
    }
}

module gabarito_raspberry() {
    echo("Gerando Gabarito Raspberry Pi...");
    
    difference() {
        // Base do gabarito
        cube([gabarito_largura, gabarito_profundidade, gabarito_altura]);
        
        // Contorno do Raspberry Pi
        translate([3, 3, 0]) {
            cube([44, 44, gabarito_altura + 1]);
            
            // Furos dos pinos GPIO (perímetro)
            // Lado esquerdo
            for (i = [0:19]) {
                y = 2 + i * 2.54;
                translate([2, y, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 1, $fn = 8);
                }
            }
            
            // Lado direito
            for (i = [0:19]) {
                y = 2 + i * 2.54;
                translate([42, y, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 1, $fn = 8);
                }
            }
            
            // Lado inferior
            for (i = [0:19]) {
                x = 2 + i * 2.54;
                translate([x, 2, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 1, $fn = 8);
                }
            }
        }
        
        // Furos de montagem
        for (x = [8, gabarito_largura - 8]) {
            for (y = [8, gabarito_profundidade - 8]) {
                translate([x, y, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 3.5, $fn = 20);
                }
            }
        }
    }
    
    // Indicação de posição
    color("red") {
        translate([gabarito_largura/2 - 10, gabarito_profundidade - 5, gabarito_altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text("RPi", size = 3, font = "Arial:style=Bold");
            }
        }
    }
}

module gabarito_motor() {
    echo("Gerando Gabarito Motor...");
    
    difference() {
        // Base do gabarito
        cube([gabarito_largura, gabarito_profundidade, gabarito_altura]);
        
        // Contorno do motor NEMA17
        translate([3, 3, 0]) {
            cube([44, 44, gabarito_altura + 1]);
            
            // Eixo central
            translate([22, 22, -1]) {
                cylinder(h = gabarito_altura + 2, d = 5, $fn = 20);
            }
            
            // Furos de fixação (4 cantos)
            for (x = [5, 37]) {
                for (y = [5, 37]) {
                    translate([x, y, -1]) {
                        cylinder(h = gabarito_altura + 2, d = 2, $fn = 15);
                    }
                }
            }
        }
        
        // Furos de montagem
        for (x = [8, gabarito_largura - 8]) {
            for (y = [8, gabarito_profundidade - 8]) {
                translate([x, y, -1]) {
                    cylinder(h = gabarito_altura + 2, d = 3.5, $fn = 20);
                }
            }
        }
    }
    
    // Indicação de posição
    color("orange") {
        translate([gabarito_largura/2 - 8, gabarito_profundidade - 5, gabarito_altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text("Motor", size = 3, font = "Arial:style=Bold");
            }
        }
    }
}

module suporte_cabos_lateral() {
    echo("Gerando Suporte de Cabos Lateral...");
    
    largura = 15;
    profundidade = 60;
    altura = 10;
    
    difference() {
        cube([largura, profundidade, altura]);
        
        // Canal principal
        translate([5, 5, 0]) {
            cube([5, profundidade - 10, altura + 1]);
        }
        
        // Furos para saída de cabos
        for (i = [0:5]) {
            y = 10 + i * 8;
            translate([7.5, y, -1]) {
                cylinder(h = altura + 2, d = 4, $fn = 15);
            }
        }
        
        // Furos de montagem
        for (y = [10, profundidade - 10]) {
            translate([largura/2, y, -1]) {
                cylinder(h = altura + 2, d = 3.5, $fn = 20);
            }
        }
    }
    
    // Presilhas para cabos
    for (i = [0:4]) {
        y = 15 + i * 8;
        translate([0, y, altura/2]) {
            // Presilha
            cube([2, 4, 2]);
        }
    }
}

module separador_compartimentos() {
    echo("Gerando Separador de Compartimentos...");
    
    largura = 100;
    profundidade = 80;
    altura = 20;
    
    difference() {
        cube([largura, profundidade, altura]);
        
        // 3 compartimentos
        compartment1 = [5, 5, 40, 70];
        compartment2 = [50, 5, 20, 70];
        compartment3 = [75, 5, 20, 70];
        
        // Rebaixos dos compartimentos
        for (comp = [compartment1, compartment2, compartment3]) {
            translate([comp[0], comp[1], 0]) {
                cube([comp[2], comp[3], 3]);
            }
        }
        
        // Furos de drenagem
        for (x = [10:20:90]) {
            for (y = [10:20:70]) {
                translate([x, y, -1]) {
                    cylinder(h = altura + 2, d = 2, $fn = 10);
                }
            }
        }
    }
    
    // Etiquetas dos compartimentos
    compartment_labels = ["ESP32", "ARDUINO", "RPi"];
    compartment_x = [25, 60, 85];
    
    for (i = [0:2]) {
        translate([compartment_x[i], 75, altura + 0.1]) {
            linear_extrude(height = 0.3) {
                text(compartment_labels[i], size = 3, font = "Arial:style=Bold");
            }
        }
    }
}

// ====================
// CHAMADA DOS MÓDULOS
// ====================

// Posicionamento para impressão
// Usei offsets para posicionar tudo em uma única print ou separadas

// Plataforma giratória (primeiro item)
translate([0, 0, 0]) {
    plataforma_giratoria();
}

// Organizador de cabos (segundo item)
translate([70, 0, 0]) {
    organizador_cabos();
}

// Gabaritos (terceiro item)
translate([0, 70, 0]) {
    gabarito_esp32();
}

translate([55, 70, 0]) {
    gabarito_arduino();
}

translate([0, 125, 0]) {
    gabarito_raspberry();
}

translate([55, 125, 0]) {
    gabarito_motor();
}

// Suporte lateral de cabos (sexto item)
translate([110, 0, 0]) {
    suporte_cabos_lateral();
}

// Separador de compartimentos (sétimo item)
translate([130, 0, 0]) {
    separador_compartimentos();
}

// ====================
// GUIAS DE IMPRESSÃO
// ====================

echo("=== SISTEMA DE SUPORTES AUXILIARES 3dPot ===");
echo("Geração de 7 componentes auxiliares:");
echo("1. Plataforma Giratória QC (60x60mm)");
echo("2. Organizador de Cabos (100x30mm)");
echo("3. Gabarito ESP32 (50x50mm)");
echo("4. Gabarito Arduino (50x50mm)");
echo("5. Gabarito Raspberry Pi (50x50mm)");
echo("6. Gabarito Motor (50x50mm)");
echo("7. Suporte Lateral de Cabos (15x60mm)");
echo("8. Separador de Compartimentos (100x80mm)");
echo(" ");
echo("RECOMENDAÇÕES DE IMPRESSÃO:");
echo("- Altura de camada: 0.15-0.2mm");
echo("- Infill: 30% para peças leves, 50% para resistência");
echo("- Suporte: Não necessário (design otimizado)");
echo("- Material: PETG para peças mecânicas, PLA para gabaritos");
echo("- Velocidade: 45-50mm/s");
echo(" ");
echo("TEMPO ESTIMADO TOTAL: 2-3 horas");
echo("FILAMENTO NECESSÁRIO: ~150g");