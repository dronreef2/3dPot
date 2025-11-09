# Guia de Contribuição - 3D Pot

Obrigado por interesse em contribuir para o projeto 3D Pot! Este guia explica como você pode participar do desenvolvimento.

## 🎯 Visão do Projeto

O 3D Pot é uma coleção de projetos Maker que combinam hardware de baixo custo com impressão 3D e software open-source, democratizando o acesso a tecnologias de automação e IoT.

## 📋 Como Contribuir

### 1. Tipos de Contribuição

- **🐛 Relatar Bugs**: Encontrou um problema? Abra uma Issue
- **💡 Sugerir Melhorias**: Ideias para novos recursos
- **📝 Melhorar Documentação**: Corrigir erros ou adicionar conteúdo
- **💻 Código**: Implementar novas funcionalidades
- **🎨 Modelos 3D**: Criar novos designs em OpenSCAD
- **🔧 Guias**: Escrever tutoriais ou guias

### 2. Antes de Começar

1. **Verifique Issues Existentes**: Procure por problemas ou funcionalidades já discutidas
2. **Crie uma Issue**: Descreva sua ideia ou problema encontrado
3. **Discuta com a Equipe**: Garanta que sua contribuição está alinhada com o projeto

### 3. Estrutura do Repositório

```
3dPot/
├── README.md                 # Documentação principal
├── CONTRIBUTING.md          # Este arquivo
├── setup-3dpot.sh          # Script de instalação automatizada
├── projetos/               # Documentação dos projetos
│   ├── esp32/             # Projetos com ESP32
│   ├── arduino/           # Projetos com Arduino
│   ├── raspberry-pi/      # Projetos com Raspberry Pi
│   └── toolchain/         # Documentação do toolchain
├── codigos/               # Código fonte
│   ├── esp32/            # Códigos ESP32/ESP8266
│   ├── arduino/          # Códigos Arduino
│   └── raspberry-pi/     # Códigos Python para Raspberry Pi
└── modelos-3d/           # Modelos 3D em OpenSCAD
    ├── esp32-projetos/
    ├── arduino-projetos/
    └── raspberry-pi-projetos/
```

## 🛠️ Desenvolvimento

### Setup do Ambiente

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/dronreef2/3dPot.git
   cd 3dPot
   ```

2. **Execute o setup automático**:
   ```bash
   chmod +x setup-3dpot.sh
   ./setup-3dpot.sh
   ```

3. **Configure o ambiente de desenvolvimento**:
   ```bash
   source ~/3dpot-workspace/dev-setup.sh
   ```

### Padrões de Código

#### C++ (Arduino/ESP32)
```cpp
// Use comentários claros
void setup() {
    // Inicialização
    Serial.begin(9600);
}

// Funções com nomes descritivos
void processarSensorLuminosidade() {
    // Implementação
}
```

#### Python (Raspberry Pi)
```python
def process_image(self, image_path: str) -> dict:
    """
    Processa uma imagem para detecção de defeitos.
    
    Args:
        image_path: Caminho para a imagem
        
    Returns:
        Dicionário com resultados da análise
    """
    # Implementação
    pass
```

#### OpenSCAD (Modelos 3D)
```openscad
// Parâmetros configuráveis no início
width = 100;
height = 50;
thickness = 3;

// Módulos reutilizáveis
module support_bracket(size) {
    // Implementação
}
```

### Convenções de Commit

Use mensagens de commit claras e descritivas:

```
tipo: descrição curta

Corpo da mensagem explicando o que e por que.
```

Tipos de commit:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação de código
- `refactor`: Refatoração
- `test`: Adicionar/alterar testes
- `chore`: Tarefas de manutenção

Exemplos:
```
feat: adicionar projeto de liquid handler automático
docs: melhorar guia de instalação do FreeCAD
fix: corrigir erro de calibragem no sensor HX711
refactor: simplificar lógica de detecção de defeitos
```

## 🐛 Relatório de Bugs

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

**Comportamento Esperado**
Descrição do que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente**
- OS: [e.g. Ubuntu 20.04]
- Hardware: [e.g. ESP32 DevKit]
- Software: [e.g. Arduino IDE 2.x]

**Informações Adicionais**
Qualquer outra informação relevante.
```

## 💡 Sugestões de Melhorias

### Template de Feature Request

```markdown
**Problema que Resolve**
Descrição do problema que esta funcionalidade resolveria.

**Solução Proposta**
Descrição da solução que você tem em mente.

**Alternativas Consideradas**
Outras soluções que você considerou.

**Informações Adicionais**
Screenshots, mockups, ou qualquer contexto adicional.
```

## 📝 Padrões de Documentação

### Documentação de Projetos

Cada projeto deve incluir:

```markdown
# Nome do Projeto

## Descrição
Descrição clara do que o projeto faz.

## Componentes Necessários
- Lista de componentes
- Custo estimado
- Onde comprar

## Funcionamento
Explicação do funcionamento técnico.

## Características Técnicas
- Tensão de operação
- Conectividade
- Precisão
- Limitações

## Montagem
Passos detalhados de montagem.

## Programação
Links para códigos e bibliotecas.

## Testes
Como testar o funcionamento.
```

### Códigos Comentados

```cpp
// Exemplo de código bem comentado
#include <Biblioteca.h>

// Pinos configuráveis
const int SENSOR_PIN = A0;    // Pino do sensor
const int LED_PIN = 13;       // Pino do LED indicador

// Constantes do sistema
const float CALIBRATION_FACTOR = 2.0;  // Fator de calibração

// Variáveis globais
float sensorValue = 0;
bool systemActive = false;

/**
 * Inicializa o sistema
 * Configura pinos e comunicação serial
 */
void setup() {
    // Configuração dos pinos
    pinMode(SENSOR_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
    
    // Inicializa comunicação
    Serial.begin(9600);
    
    // Mensagem de inicialização
    Serial.println("Sistema iniciado");
}

/**
 * Loop principal do programa
 */
void loop() {
    // Lê sensor
    sensorValue = analogRead(SENSOR_PIN);
    
    // Processa leitura
    processSensor();
    
    // Atualiza LEDs
    updateLEDs();
    
    // Aguarda próximo ciclo
    delay(100);
}
```

## 🎨 Modelos 3D

### Padrões OpenSCAD

1. **Parâmetros no início**: Todos os valores configuráveis
2. **Módulos reutilizáveis**: Para componentes comuns
3. **Comentários**: Explicar parâmetros e funções
4. **Organização**: Separar seções com módulos

```openscad
// ============================================
// PARÂMETROS CONFIGURÁVEIS
// ============================================
width = 100;          // Largura total
height = 50;          // Altura total
thickness = 3;        // Espessura das paredes

// ============================================
// MÓDULOS PRINCIPAIS
// ============================================

// Corpo principal do componente
module main_body() {
    // Implementação
}

// Suporte para montagem
module mounting_holes() {
    // Implementação
}

// ============================================
// ASSEMBLY
// ============================================
translate([0, 0, 0]) {
    main_body();
    mounting_holes();
}
```

## 🧪 Testes

### Testes de Hardware

Para cada projeto, inclua:

1. **Teste individual de componentes**
2. **Teste de integração**
3. **Teste de cenários extremos**
4. **Teste de calibração**

### Testes de Software

```python
import unittest
from your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        self.instance = YourClass()
    
    def test_function(self):
        result = self.instance.function()
        self.assertEqual(result, expected_value)
    
    def test_edge_case(self):
        # Teste de caso extremo
        pass

if __name__ == '__main__':
    unittest.main()
```

## 📦 Estrutura de Pull Requests

### Template de PR

```markdown
## 📋 Resumo
Descrição breve das mudanças.

## 🔍 Detalhes
- **Tipo de mudança**: (correção de bug, nova funcionalidade, etc.)
- **Componentes afetados**: (ESP32, Arduino, Raspberry Pi, etc.)
- **Breaking Changes**: (se aplicável)

## ✅ Checklist
- [ ] Código testado em hardware real
- [ ] Documentação atualizada
- [ ] Modelos 3D incluídos (se aplicável)
- [ ] Testes escritos
- [ ] Commits bem formatados

## 🧪 Testes Realizados
- [ ] Teste 1
- [ ] Teste 2
- [ ] Teste 3

## 📸 Screenshots
(Se aplicável)
```

## 🎯 Prioridades do Projeto

1. **Estabilidade**: Código bem testado e documentado
2. **Acessibilidade**: Hardware barato e fácil de encontrar
3. **Modularidade**: Componentes reutilizáveis
4. **Documentação**: Guias claros e exemplos práticos
5. **Comunidade**: Inclusivo e colaborativo

## 🤝 Código de Conduta

### Nosso Compromisso

Nos comprometemos em manter um ambiente acolhedor e inclusivo para todos, independentemente de experiência, gênero, identidade, orientação sexual, handicap, aparência física, etnia, ou religião.

### Comportamentos Esperados

- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista
- Aceitar críticas construtivas graciosamente
- Focar no melhor para a comunidade
- Demonstrar empatia com outros membros

### Comportamentos Inaceitáveis

- Uso de linguagem ou imagens sexualizadas
- Trolling, insultos, ataques pessoais/políticos
- Assédio público ou privado
- Publicar informações privadas de outros sem permissão
- Conduta inapropriada em contexto profissional

## 📞 Suporte

### Onde Pedir Ajuda

- **GitHub Issues**: Para bugs e sugestões
- **Discussões**: Para perguntas gerais
- **Wiki**: Para documentação detalhada

### Como Solicitar Suporte

1. Pesquise problemas similares
2. Forneça informações detalhadas
3. Inclua logs e screenshots
4. Teste as soluções sugeridas

## 🏆 Reconhecimento

Contribuidores serão reconhecidos em:
- README.md principal
- Release notes
- Site do projeto (quando houver)

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto.

---

Obrigado por fazer parte da comunidade 3D Pot! 🚀
