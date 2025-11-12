# 3dPot Modelos 3D Paramétricos - Guia Completo

**Autor:** MiniMax Agent  
**Data:** 2025-11-12  
**Versão:** 2.0  

## 📋 VISÃO GERAL

O projeto 3dPot inclui modelos 3D **totalmente paramétricos** em OpenSCAD, permitindo customização completa para diferentes dispositivos e aplicações. Este guia explica como usar, modificar e imprimir estes modelos.

## 🎯 MODELOS DISPONÍVEIS

### 1. **Universal Case Paramétrico** (`universal-case-parametric.scad`)
- **Para que serve:** Case universal para ESP32, Arduino, Raspberry Pi
- **Parâmetros principais:** Dimensões do dispositivo, tipo de tampa, ventilação
- **Recursos:** Snap fits, montagem em parede, pés de borracha, fan mount

### 2. **Suporte Monitor de Filamento** (`suporte-monitor-filamento.scad`)
- **Para que serve:** Suporte específico para ESP32 com sensor de peso
- **Parâmetros:** Dimensões ESP32, dimensões base, posições sensores
- **Recursos:** Pinos de fixação, alojamento sensor, ventilação

### 3. **Rolo Esteira Transportadora** (`rola-esteira.scad`)
- **Para que serve:** Rolos para sistemas transportadores
- **Parâmetros:** Comprimento, diâmetro, padrão superfície
- **Recursos:** Flanges, furos para parafusos, padrão tração

## 🛠️ COMO USAR OS PARÂMETROS

### **Passo 1: Abrir o Arquivo**
1. Baixe e instale o [OpenSCAD](https://www.openscad.org/)
2. Abra o arquivo `.scad` desejado
3. O código será renderizado automaticamente

### **Passo 2: Modificar Parâmetros**
```openscad
// Encontre a seção "PARÂMETROS CUSTOMIZÁVEIS" 
// e modifique as variáveis:

// Exemplo para Universal Case:
device_width = 30.0;      // Largura do seu dispositivo
device_length = 55.0;     // Comprimento do seu dispositivo
device_height = 10.0;     // Altura do seu dispositivo

lid_type = "snap";        // Tipo de tampa: "snap", "screw", "hinge"
ventilation_enabled = true; // Habilitar ventilação
wall_mount = false;       // Montagem em parede
```

### **Passo 3: Renderizar**
- Pressione **F6** ou vá em `View → Render`
- Aguarde o processamento (pode demorar alguns segundos)
- Visualize o resultado

### **Passo 4: Exportar STL**
- Vá em `File → Export → Export as STL`
- Salve o arquivo `.stl` para impressão 3D

## 📐 PARÂMETROS DETALHADOS

### **Universal Case Paramétrico**

| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| `device_width` | 10-100mm | Largura do dispositivo |
| `device_length` | 10-100mm | Comprimento do dispositivo |
| `device_height` | 5-50mm | Altura do dispositivo |
| `wall_thickness` | 1-5mm | Espessura das paredes |
| `clearance` | 0.5-2mm | Folga ao redor do dispositivo |
| `lid_type` | snap/screw/hinge/slide/none | Tipo de tampa |
| `ventilation_enabled` | true/false | Habilitar furos de ventilação |
| `fan_mount` | true/false | Montagem para ventilador 40x40mm |
| `wall_mount` | true/false | Suporte para montagem em parede |
| `desk_stand` | true/false | Suporte para mesa |

### **Suporte Monitor Filamento**

| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| `esp32_width` | 20-40mm | Largura do ESP32 |
| `esp32_length` | 40-70mm | Comprimento do ESP32 |
| `base_width` | 25-50mm | Largura da base |
| `base_length` | 60-90mm | Comprimento da base |
| `pin_diameter` | 2-5mm | Diâmetro dos pinos de fixação |
| `sensor_hole_diameter` | 5-15mm | Diâmetro do furo para sensor |

### **Rolo Esteira**

| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| `roller_length` | 50-200mm | Comprimento do rolo |
| `roller_diameter` | 20-50mm | Diâmetro do rolo |
| `shaft_diameter` | 5-15mm | Diâmetro do eixo |
| `flange_thickness` | 5-15mm | Espessura dos flanges |
| `surface_pattern` | true/false | Padrão para tração |

## 🖨️ CONFIGURAÇÕES DE IMPRESSÃO

### **Material Recomendado**
- **PLA:** Fácil impressão, boa qualidade
- **PETG:** Mais resistente, ideal para peças funcionais
- **ABS:** Resistente ao calor (para aplicações industriais)

### **Configurações por Tipo de Peça**

#### **Cases e Suportes:**
```
Altura de camada: 0.2mm
Velocidade: 50mm/s
Temperatura PLA: 200-220°C
Temperatura PETG: 230-250°C
Infill: 20-30%
Suporte: Desnecessário
```

#### **Peças Mecânicas (Rolos, Engrenagens):**
```
Altura de camada: 0.15mm
Velocidade: 40mm/s
Temperatura PETG: 240-250°C
Infill: 50-80%
Suporte: Conforme necessário
```

#### **Peças de Precisão:**
```
Altura de camada: 0.1-0.15mm
Velocidade: 30-40mm/s
Temperatura: conforme material
Infill: 40-60%
Suporte: Recomendado para overhangs
```

## 🔧 PÓS-PROCESSAMENTO

### **Limppeza Geral**
1. **Remova suportes** com alicate de bico
2. **Lixe levemente** superfícies com lixa 400-600 grit
3. **Limpe furos** com broca do tamanho adequado
4. **Teste montagens** antes da aplicação final

### **Tratamento de Superfície**
- **Para acabamento liso:** Primer + lixa fina + tinta
- **Para resistência:** Laca ou verniz
- **Para impressão 3D perfeita:** Acetona (ABS apenas)

### **Montagem de Snap Fits**
1. **Teste snap fits** manualmente
2. **Ajuste tolerância** se muito apertado/folgado
3. **Use lima** para ajustar abertura

## 📱 EXEMPLOS PRÁTICOS

### **Exemplo 1: Case para ESP32 DevKit v1**
```openscad
device_width = 25.0;      // ESP32 DevKit v1
device_length = 55.0;
device_height = 3.2;

wall_thickness = 2.0;
clearance = 1.0;
lid_type = "snap";
ventilation_enabled = true;
wall_mount = true;
```

### **Exemplo 2: Case para Raspberry Pi 4**
```openscad
device_width = 85.0;      // Raspberry Pi 4
device_length = 56.0;
device_height = 17.0;

wall_thickness = 3.0;
clearance = 1.5;
lid_type = "screw";
ventilation_enabled = true;
fan_mount = true;
wall_mount = true;
```

### **Exemplo 3: Case para Arduino Nano**
```openscad
device_width = 18.0;      // Arduino Nano
device_length = 45.0;
device_height = 5.0;

wall_thickness = 1.5;
clearance = 0.8;
lid_type = "slide";
ventilation_enabled = false;
desk_stand = true;
```

## 🎨 PERSONALIZAÇÃO AVANÇADA

### **Adicionar Novos Recursos**

Para adicionar recursos customizados, edite o arquivo `.scad`:

```openscad
// Adicione novos parâmetros no topo
my_custom_parameter = true;

// Adicione novo módulo
module my_custom_feature() {
    if (my_custom_parameter) {
        // Sua feature aqui
        cube([10, 10, 10]);
    }
}

// Adicione na montagem final
my_custom_feature();
```

### **Modificar Geometria Existente**

Para alterar geometria, encontre o módulo correspondente:

```openscad
// Exemplo: modificar base_box
module base_box() {
    difference() {
        // Modifique as dimensões externas
        cube([external_width, external_length, external_height]);
        
        // Modifique os recortes
        translate([wall_thickness/2, wall_thickness/2, base_thickness]) {
            // Nova geometria interna
            cube([device_width + clearance, device_length + clearance, device_height + lid_gap]);
        }
    }
}
```

## 🔍 RESOLUÇÃO DE PROBLEMAS

### **Problema: Snap Fit não Funciona**
**Solução:**
- Reduza `snap_tolerance` para menos folga
- Aumente a flexibilidade da tampa
- Use material mais flexível (PETG)

### **Problema: Ventilação Inadequada**
**Solução:**
- Aumente `ventilation_spacing`
- Reduza `ventilation_hole_diameter`
- Adicione fan mount para resfriamento ativo

### **Problema: Dimensões não Batem**
**Solução:**
- Meça seu dispositivo com paquímetro
- Ajuste `clearance` conforme necessário
- Considere tolerâncias de impressão

### **Problema: Modelo não Renderiza**
**Solução:**
- Verifique sintaxe do OpenSCAD
- Reduza complexidade temporariamente
- Use `F5` para preview antes do `F6`

## 📚 RECURSOS ADICIONAIS

### **Downloads e Links**
- [OpenSCAD Software](https://www.openscad.org/)
- [Biblioteca de Casos](https://www.thingiverse.com/)
- [Tutorial OpenSCAD](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)

### **Comunidades**
- [OpenSCAD Community Forum](https://forum.openscad.org/)
- [r/3Dprinting Reddit](https://reddit.com/r/3Dprinting)
- [3dPot Project Repository](https://github.com/dronreef2/3dPot)

## 🚀 PRÓXIMOS PASSOS

1. **Experimente** com diferentes parâmetros
2. **Imprima** um modelo simples primeiro
3. **Teste** a montagem e ajuste
4. **Compartilhe** suas variações
5. **Contribua** com novos designs

---

**⭐ Lembre-se:** Os modelos 3D paramétricos são a base da flexibilidade do projeto 3dPot. Compreender como modificá-los permite adaptar o sistema para qualquer aplicação específica!