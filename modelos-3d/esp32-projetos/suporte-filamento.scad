// Monitor de Filamento - Suporte da Célula de Carga
// Projeto: 3D Pot
// Autor: MiniMax Agent

// Parâmetros configuráveis
diameter = 200;           // Diâmetro interno do suporte (mm)
wall_thickness = 3;       // Espessura da parede (mm)
base_thickness = 5;       // Espessura da base (mm)
arm_length = 80;          // Comprimento do braço de alavanca (mm)
arm_width = 20;           // Largura do braço (mm)
arm_thickness = 5;        // Espessura do braço (mm)
sensor_hole_diameter = 10; // Diâmetro do furo para o sensor (mm)

// Altura total
total_height = base_thickness + 50;

// Translação para centralizar na origem
translate([0, 0, total_height/2]) {
    
    // Base principal
    difference() {
        cylinder(d=diameter + 2*wall_thickness, h=base_thickness, center=true);
        cylinder(d=diameter, h=base_thickness + 1, center=true);
    }
    
    // Paredes do suporte
    cylinder(d=diameter + 2*wall_thickness, h=30, center=true);
    difference() {
        cylinder(d=diameter + 2*wall_thickness, h=total_height, center=true);
        cylinder(d=diameter, h=total_height + 1, center=true);
    }
    
    // Suporte central para o eixo
    cylinder(d=15, h=40, center=true);
    
    // Braço de alavanca
    translate([arm_length/2, 0, total_height - 15]) {
        // Corpo do braço
        cube([arm_length, arm_width, arm_thickness], center=true);
        
        // Extensão do braço (onde a célula de carga é montada)
        translate([arm_length/2 + 15, 0, 0]) {
            cylinder(d=20, h=arm_thickness + 2, center=true);
            
            // Furos para parafusos da célula de carga
            for(i=[0:3]) {
                angle = i * 90;
                x = 15 * cos(angle);
                y = 15 * sin(angle);
                translate([x, y, 0]) {
                    cylinder(d=3, h=arm_thickness + 4, center=true);
                }
            }
        }
    }
    
    // Furos para montagem na bancada
    for(i=[0:3]) {
        angle = i * 90 + 45;
        x = (diameter/2 + wall_thickness + 10) * cos(angle);
        y = (diameter/2 + wall_thickness + 10) * sin(angle);
        translate([x, y, -total_height/2 + base_thickness/2]) {
            cylinder(d=6, h=base_thickness + 2, center=true);
        }
    }
    
    // Suporte para o ESP32
    translate([0, -(diameter/2 + wall_thickness + 15), total_height/2 - 10]) {
        difference() {
            cube([50, 30, 20], center=true);
            // Furos para parafusos
            for(i=[0:3]) {
                x = (i % 2) * 40 - 20;
                y = (i < 2) * 20 - 10;
                translate([x, y, 0]) {
                    cylinder(d=2, h=22, center=true);
                }
            }
        }
    }
}

// Adiciona texto informativo
module add_info_text() {
    translate([0, -diameter/2 - 30, 0]) {
        linear_extrude(height=1) {
            text("Monitor de Filamento", size=8, halign="center");
            translate([0, -12, 0]) {
                text("3D Pot Project", size=6, halign="center");
            }
        }
    }
}

add_info_text();
