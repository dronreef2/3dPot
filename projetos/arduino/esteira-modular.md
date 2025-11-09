# Mini Esteira Transportadora Modular com Arduino

## Descrição
Sistema automatizado de movimentação de peças usando motor de passo e sensores de detecção.

## Componentes Necessários
- Arduino Uno/Nano
- Motor de passo NEMA17 ou motor DC com encoder
- Driver de motor (A4988 para passo, L298N para DC)
- Sensores infravermelhos (IR)
- Barreira de luz (opcional)
- Switches de fim de curso
- LED de status

## Funcionamento
1. Motor movimenta a esteira com velocidade controlada
2. Sensores IR detectam presença de objetos
3. Sistema para automaticamente ao detectar objeto
4. Pode acionar outros dispositivos (braço robótico, etc.)
5. Interface serial para controle manual

## Características Técnicas
- Controle: PWM para motor DC, step/dir para motor de passo
- Velocidade: Ajustável via potenciômetro
- Carga máxima: 2kg (dependendo do motor)
- Tensão: 12V para motor + 5V para lógica
