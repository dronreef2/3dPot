# Monitor de Filamento Universal com ESP32

## Descrição
Sistema inteligente para monitorar a quantidade de filamento restante em carretéis, usando célula de carga e ESP32 com conectividade Wi-Fi.

## Componentes Necessários
- ESP32 DevKit
- Célula de carga (HX711) + plataforma
- Resistores pull-up/pull-down (10kΩ)
- Protoboard ou PCB
- Cabo USB para programação
- Fios jumper

## Funcionamento
1. A célula de carga mede o peso do carretel
2. O ESP32 subtrai o peso do carretel vazio (calibração inicial)
3. Calcula a porcentagem de filamento restante
4. Expõe os dados via interface web ou MQTT
5. Integrado com Home Assistant ou outras plataformas IoT

## Características Técnicas
- Conectividade: Wi-Fi
- Interface: Web Server
- Precisão: ±1g (dependendo da célula)
- Alimentação: 5V USB
- Comunicação: MQTT, HTTP REST
