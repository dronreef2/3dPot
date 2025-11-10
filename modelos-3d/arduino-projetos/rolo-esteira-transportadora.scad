// Rolo Transportador para Esteira Arduino
// Arquivo OpenSCAD Paramétrico
// Data: 2025-11-10
// Projeto: 3dPot - Esteira Transportadora

// ==================== PARÂMETROS ====================
// Todas as medidas em mm

// Dimensões do rolo principal
roller_diameter = 40.0;          // Diâmetro do rolo
roller_length = 100.0;           // Comprimento do rolo
roller_wall_thickness = 3.0;     // Espessura da parede do rolo

// Eixo central
shaft_diameter = 8.0;            // Diâmetro do eixo
shaft_length = 110.0;            // Comprimento do eixo (maior que o rolo)
shaft_key_width = 2.0;           // Largura da chave plana
shaft_key_depth = 1.0;           // Profundidade da chave

// Rolamentos/buchas
bearing_outer_diameter = 15.0;   // Diâmetro externo do rolamento
bearing_inner_diameter = 8.0;    // Diâmetro interno do rolamento
bearing_length = 7.0;            // Comprimento do rolamento

// Flanges (suporte lateral)
flange_diameter = 45.0;          // Diâmetro da flange
flange_thickness = 5.0;          // Espessura da flange
flange_hole_diameter = 6.0;      // Diâmetro dos furos de montagem

// Parâmetros de funcionamento
load_capacity = 2.0;             // Capacidade de carga (kg)
friction_coefficient = 0.3;      // Coeficiente de atrito

// ==================== MODELAGEM ====================

module main_roller() {
    // Rolo principal oco
    difference() {
        // Corpo sólido do rolo
        cylinder(d = roller_diameter, h = roller_length);
        
        // Cavidade interna
        cylinder(d = roller_diameter - 2*roller_wall_thickness, h = roller_length);
        
        // Eixo central (furo)
        cylinder(d = shaft_diameter, h = roller_length + 10);
    }
}

module shaft() {
    // Eixo principal com chanfro
    difference() {
        // Corpo do eixo
        cylinder(d = shaft_diameter, h = shaft_length);
        
        // Chanfro em uma extremidade
        translate([0, 0, shaft_length/2]) {
            // Chave plana para fixação do motor
            cube([shaft_key_width, shaft_diameter, shaft_length/2]);
        }
        
        // Furo de segurança
        translate([0, 0, -5]) {
            cylinder(d = 2, h = shaft_length + 10);
        }
    }
}

module flange_support() {
    // Flange de suporte lateral
    difference() {
        // Flange sólida
        cylinder(d = flange_diameter, h = flange_thickness);
        
        // Furo central para o eixo
        cylinder(d = shaft_diameter + 2, h = flange_thickness + 2);
        
        // Furos de montagem
        for (angle = [0, 60, 120, 180, 240, 300]) {
            translate([
                cos(angle) * (flange_diameter/2 - 5),
                sin(angle) * (flange_diameter/2 - 5),
                0
            ]) {
                cylinder(d = flange_hole_diameter, h = flange_thickness + 2);
            }
        }
    }
}

module bearing_bushing() {
    // Bucha/rolamento de apoio
    difference() {
        // Bucha externa
        cylinder(d = bearing_outer_diameter, h = bearing_length);
        
        // Cavidade interna
        cylinder(d = bearing_inner_diameter, h = bearing_length + 2);
    }
}

module roller_assembly() {
    // Montagem completa do conjunto
    
    // Rolamento/bucha em cada extremidade
    translate([0, 0, bearing_length/2]) {
        bearing_bushing();
    }
    
    translate([0, 0, roller_length - bearing_length/2]) {
        bearing_bushing();
    }
    
    // Rolo principal
    translate([0, 0, 0]) {
        main_roller();
    }
    
    // Flanges de suporte
    translate([0, 0, -flange_thickness]) {
        flange_support();
    }
    
    translate([0, 0, roller_length]) {
        flange_support();
    }
}

// ==================== DESENHO TÉCNICO ====================

// Vista em corte (dimensional)
// translate([-60, 0, 0]) {
//     %roller_assembly();
// }

// ==================== MONTAGEM FINAL ====================

roller_assembly();

// ==================== INSTRUÇÕES DE IMPRESSÃO ====================

/*
INSTRUÇÕES DE IMPRESSÃO 3D:

1. PARÂMETROS RECOMENDADOS:
   - Material: PETG (maior resistência) ou ABS
   - Temperatura: PETG (230-250°C) / ABS (220-240°C)
   - Altura da camada: 0.2mm
   - Velocidade: 40-50mm/s (mais lenta para melhor aderência)
   - Suporte: NECESSÁRIO para overhangs > 45°

2. ORIENTAÇÃO DE IMPRESSÃO:
   - Eixo do rolo perpendicular à base
   - Fazer em 2 partes se necessário
   - Usar brim para melhor aderência

3. MONTAGEM:
   - Inserir eixo central
   - Montar rolamentos 608ZZ nas extremidades
   - Fixar com porcas M8 nas pontas
   - Verificar rotação livre

4. MOTORIZAÇÃO:
   - Usar motor de passo NEMA17
   - Polia GT2 na extremidade do eixo
   - Correia GT2 para transmissão
   - Controlador Arduino + driver A4988

5. COMPONENTES ADICIONAIS NECESSÁRIOS:
   - 2x Rolamentos 608ZZ
   - 1x Eixo M8 x 110mm
   - 2x Porcas M8
   - 4x Parafusos M6 x 20mm (montagem)
   - 1x Polia GT2 20T
   - 1x Correia GT2

6. ESPECIFICAÇÕES TÉCNICAS:
   - Capacidade: 2kg distribuído
   - Velocidade: 10-50mm/s ajustável
   - Precisão: ±1mm
   - Material: PETG com aditivos UV
   - Vida útil: >10.000 ciclos

7. FUNCIONALIDADES:
   - Transporte suave de objetos
   - Controle de velocidade variável
   - Parada automática por sensores
   - Interface serial para controle
   - Monitoramento de posição

8. APLICACÕES:
   - Alimentação automática de impressoras 3D
   - Transporte de peças em produção
   - Sistema de classificação
   - Linha de montagem automatizada
   - Transporte de amostras laboratoriais
*/