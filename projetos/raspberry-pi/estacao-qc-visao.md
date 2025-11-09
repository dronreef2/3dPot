# Estação de Controle de Qualidade com Visão Computacional

## Descrição
Sistema automatizado de inspeção de peças usando Raspberry Pi, câmera e algoritmos de visão computacional.

## Componentes Necessários
- Raspberry Pi 4 (2GB mínimo)
- Câmera Pi HQ ou USB
- LED ring para iluminação
- Motor de passo NEMA17 + driver
- Arduino (opcional, para controle preciso do motor)
- Caixa impressão 3D para proteção
- Suporte ajustável para câmera

## Funcionamento
1. Motor gira a peça 360° em múltiplas posições
2. Câmera captura imagens em cada posição
3. Algoritmo OpenCV analisa cada imagem
4. Comparação com modelo de referência 3D
5. Detecção de defeitos: camadas faltando, warping, etc.
6. Resultado exibido no dashboard web
7. Aprovado/Reprovado com nível de confiança

## Características Técnicas
- Processamento: OpenCV, Python
- Conectividade: Dashboard web com Flask
- Precisão: 0.5mm (dependendo da câmera)
- Tempo de inspeção: 30-60s por peça
- Iluminação: LED controlado automaticamente
