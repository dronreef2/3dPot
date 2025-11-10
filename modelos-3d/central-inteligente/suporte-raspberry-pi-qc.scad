// Suporte para Raspberry Pi 4 + Estação QC
// Inclui furação para câmera, motor de passo e LEDs de iluminação

// Dimensões do Raspberry Pi 4
rpi_largura = 58;      // 5.8cm
rpi_profundidade = 58; // 5.8cm
rpi_altura = 4;        // 0.4cm

// Dimensões do suporte
suporte_largura = 80;
suporte_profundidade = 80;
suporte_altura = 10;

// Layout dos componentes
rpi_offset_x = (suporte_largura - rpi_largura) / 2;
rpi_offset_y = 20;  // Posicionamento ligeiramente para cima

// Área para câmera Pi HQ
camera_largura = 25;
camera_profundidade = 25;
camera_offset_x = (suporte_largura - camera_largura) / 2;
camera_offset_y = 5;

// Motor de passo (NEMA17)
motor_largura = 42;   // 4.2cm
motor_profundidade = 42;
motor_altura = 10;    // 1.0cm
motor_offset_x = 5;
motor_offset_y = 60;

// LED ring para iluminação
led_ring_diametro = 30;
led_ring_offset_x = (suporte_largura - led_ring_diametro) / 2;
led_ring_offset_y = 38;

// Furações
furo_diametro = 3.5;
furo_espacamento = 25;
margin = 12;

// GPIO headers do Raspberry Pi
gpio_espacamento = 2.54;
num_pinos_por_lado = 20;

// Conectores USB e Ethernet
conector_usb_largura = 15;
conector_usb_profundidade = 12;
conector_eth_largura = 15;
conector_eth_profundidade = 15;

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
    
    // Rebaixo para Raspberry Pi
    translate([rpi_offset_x, rpi_offset_y, 0]) {
        cube([rpi_largura, rpi_profundidade, 4]);
        
        // Furos dos pinos GPIO (4 cantos)
        for (x = [2, rpi_largura - 2]) {
            for (y = [2, rpi_profundidade - 2]) {
                translate([x, y, -1]) {
                    cylinder(h = 5, d = 1, $fn = 10);
                }
            }
        }
        
        // Furos para todos os pinos GPIO (perímetro)
        // Lado esquerdo
        for (i = [0:num_pinos_por_lado-1]) {
            y_pos = 3 + i * gpio_espacamento;
            translate([2, y_pos, -1]) {
                cylinder(h = 5, d = 1, $fn = 8);
            }
        }
        
        // Lado direito
        for (i = [0:num_pinos_por_lado-1]) {
            y_pos = 3 + i * gpio_espacamento;
            translate([rpi_largura - 2, y_pos, -1]) {
                cylinder(h = 5, d = 1, $fn = 8);
            }
        }
        
        // Lado inferior
        for (i = [0:19]) {
            x_pos = 3 + i * gpio_espacamento;
            translate([x_pos, 2, -1]) {
                cylinder(h = 5, d = 1, $fn = 8);
            }
        }
    }
}

// Rebaixo para câmera
translate([camera_offset_x, camera_offset_y, 0]) {
    difference() {
        cube([camera_largura, camera_profundidade, 3]);
        cube([camera_largura - 2, camera_profundidade - 2, 4]);
    }
    
    // Furos para lente da câmera
    translate([camera_largura/2, camera_profundidade/2, -1]) {
        cylinder(h = 4, d = 8, $fn = 20);
    }
    
    // Furos para conectores da câmera
    for (x = [5, camera_largura - 5]) {
        for (y = [5, camera_profundidade - 5]) {
            translate([x, y, -1]) {
                cylinder(h = 4, d = 1.5, $fn = 10);
            }
        }
    }
}

// Suporte para motor de passo
translate([motor_offset_x, motor_offset_y, 0]) {
    difference() {
        cube([motor_largura, motor_profundidade, 3]);
        cube([motor_largura - 2, motor_profundidade - 2, 4]);
    }
    
    // Eixo do motor
    translate([motor_largura/2, motor_profundidade/2, -1]) {
        cylinder(h = 4, d = 5, $fn = 20);
    }
    
    // Furos para montagem do motor
    for (x = [5, 37]) {  // corners do motor
        for (y = [5, 37]) {
            translate([x, y, -1]) {
                cylinder(h = 4, d = 2, $fn = 15);
            }
        }
    }
}

// LED ring para iluminação
translate([led_ring_offset_x + led_ring_diametro/2, led_ring_offset_y + led_ring_diametro/2, 0]) {
    // Base do LED ring
    difference() {
        cylinder(h = 2, d = led_ring_diametro + 2, $fn = 30);
        cylinder(h = 3, d = led_ring_diametro - 4, $fn = 30);
    }
    
    // LED ring completo
    for (i = [0:8]) {
        angle = i * 45;
        x = (led_ring_diametro/2 - 2) * cos(angle);
        y = (led_ring_diametro/2 - 2) * sin(angle);
        translate([x, y, 0]) {
            color("white") {
                cylinder(h = 1, d = 3, $fn = 15);
            }
        }
    }
}

// Rebaixos para conectores do Raspberry Pi
// Conectores USB
translate([5, 15, 0]) {
    cube([conector_usb_largura, conector_usb_profundidade, 4]);
}

translate([5, 30, 0]) {
    cube([conector_usb_largura, conector_usb_profundidade, 4]);
}

// Conector Ethernet
translate([5, 45, 0]) {
    cube([conector_eth_largura, conector_eth_profundidade, 4]);
}

// Conector HDMI
translate([suporte_largura - conector_usb_largura - 5, 15, 0]) {
    cube([conector_usb_largura, conector_usb_profundidade, 4]);
}

translate([suporte_largura - conector_usb_largura - 5, 30, 0]) {
    cube([conector_usb_largura, conector_usb_profundidade, 4]);
}

// Conector de alimentação
translate([suporte_largura - 20, 45, 0]) {
    cube([15, 10, 4]);
}

// Suporte para ventilador do Raspberry Pi
ventilador_diametro = 25;
ventilador_offset_x = rpi_offset_x + 15;
ventilador_offset_y = rpi_offset_y + 15;

translate([ventilador_offset_x, ventilador_offset_y, 0]) {
    difference() {
        cylinder(h = 3, d = ventilador_diametro, $fn = 30);
        cylinder(h = 4, d = ventilador_diametro - 10, $fn = 30);
    }
    
    // Furos para montagem do ventilador
    for (angle = [0:90:270]) {
        x = (ventilador_diametro/2 - 3) * cos(angle);
        y = (ventilador_diametro/2 - 3) * sin(angle);
        translate([x, y, -1]) {
            cylinder(h = 4, d = 2, $fn = 10);
        }
    }
}

// Canal de cabos para organização
translate([suporte_largura/2 - 20, 2, 0]) {
    cube([40, 6, 3]);
    
    // Furos para passagem de cabos
    for (i = [5:10:35]) {
        translate([i, 3, -1]) {
            cylinder(h = 5, d = 4, $fn = 15);
        }
    }
}

// Área de fixação da plataforma giratória
translate([led_ring_offset_x + 10, led_ring_offset_y + 10, 0]) {
    // Base da plataforma de inspeção
    cube([20, 20, 2]);
    
    // Furo central para eixo
    translate([10, 10, -1]) {
        cylinder(h = 4, d = 6, $fn = 20);
    }
    
    // Furos para parafusos de fixação
    for (x = [5, 15]) {
        for (y = [5, 15]) {
            translate([x, y, -1]) {
                cylinder(h = 4, d = 2, $fn = 10);
            }
        }
    }
}

// Labels identificativos
color("green") {
    translate([suporte_largura/2 - 12, 2, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("RPi QC", size = 4, font = "Arial:style=Bold");
        }
    }
    
    translate([motor_offset_x + 5, motor_offset_y + 50, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("MOTOR", size = 3, font = "Arial:style=Bold");
        }
    }
    
    translate([led_ring_offset_x + 8, led_ring_offset_y + 35, suporte_altura + 0.1]) {
        linear_extrude(height = 0.3) {
            text("LEDs", size = 3, font = "Arial:style=Bold");
        }
    }
}

// Ventilação adicional
for (i = [20:20:suporte_largura-20]) {
    translate([i, suporte_profundidade - 5, -1]) {
        cylinder(h = suporte_altura + 2, d = 4, $fn = 15);
    }
}

// Pés de borracha
for (x = [margin, suporte_largura - margin]) {
    for (y = [margin, suporte_profundidade - margin]) {
        translate([x, y, -1]) {
            cylinder(h = 2, d = 6, $fn = 20);
            translate([0, 0, 1]) {
                cylinder(h = 3, d = 3, $fn = 20);
            }
        }
    }
}

// Guia de impressão
echo("=== Suporte Raspberry Pi + Estação QC ===");
echo("Dimensões:", suporte_largura, "x", suporte_profundidade, "x", suporte_altura);
echo("Área de impressão: 85x85mm (grande!)");
echo("Suporte: Sim (múltiplas áreas)");
echo("Altura de camada: 0.15mm");
echo("Infill: 35%");
echo("Velocidade: 40mm/s");
echo("Tempo estimado: 3-4 horas");
echo("Material: PETG (resistência à temperatura)");