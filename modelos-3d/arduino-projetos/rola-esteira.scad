// Mini Esteira Transportadora - Rolo de Acionamento
// Projeto: 3D Pot
// Autor: MiniMax Agent

// Parâmetros configuráveis
roller_length = 100;      // Comprimento do rolo (mm)
roller_diameter = 30;     // Diâmetro do rolo (mm)
shaft_diameter = 8;       // Diâmetro do eixo (mm)
flange_thickness = 8;     // Espessura do flange (mm)
flange_diameter = 40;     // Diâmetro do flange
surface_pattern = true;   // Padrão de superfície para tração

// Translação para centralizar
translate([0, 0, roller_length/2]) {
    
    // Corpo principal do rolo
    difference() {
        cylinder(d=roller_diameter, h=roller_length, center=true);
        cylinder(d=shaft_diameter, h=roller_length + 2, center=true);
    }
    
    // Flanges nas extremidades
    for(end = [-1, 1]) {
        translate([0, 0, end * (roller_length/2 - flange_thickness/2)]) {
            difference() {
                cylinder(d=flange_diameter, h=flange_thickness, center=true);
                cylinder(d=shaft_diameter, h=flange_thickness + 2, center=true);
            }
            
            // Furos para parafusos de fixação
            for(i=[0:5]) {
                angle = i * 60;
                radius = flange_diameter/2 - 5;
                x = radius * cos(angle);
                y = radius * sin(angle);
                translate([x, y, 0]) {
                    cylinder(d=4, h=flange_thickness + 2, center=true);
                }
            }
        }
    }
    
    // Padrão de superfície para melhor tração
    if (surface_pattern) {
        for(i=[0:roller_length-1]) {
            translate([0, 0, i - roller_length/2 + 0.5]) {
                // Padrão em X
                for(j=[0:15]) {
                    angle = j * 22.5;
                    x = (roller_diameter/2 - 1) * cos(angle);
                    y = (roller_diameter/2 - 1) * sin(angle);
                    translate([x, y, 0]) {
                        cylinder(d=1, h=2, center=true);
                    }
                }
            }
        }
    }
    
    // Marcadores de posição
    for(i=[0:3]) {
        angle = i * 90;
        x = (roller_diameter/2 + 2) * cos(angle);
        y = (roller_diameter/2 + 2) * sin(angle);
        translate([x, y, 0]) {
            cylinder(d=3, h=3, center=true);
        }
    }
}

// Adiciona informações
module add_info() {
    translate([0, -roller_diameter/2 - 20, 0]) {
        linear_extrude(height=1) {
            text("Rolo Esteira", size=6, halign="center");
            translate([0, -8, 0]) {
                text(str(roller_length) + "mm", size=4, halign="center");
            }
        }
    }
}

add_info();
