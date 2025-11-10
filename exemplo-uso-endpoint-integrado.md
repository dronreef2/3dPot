# 🤖 Exemplo de Uso - Endpoint Integrado LGM

## 🎯 Endpoint Principal: `/api/lgm/projeto-completo`

Este endpoint especial **integra tudo**: recebe um texto e retorna o projeto completo com modelo 3D + análise + orçamento.

## 📡 Como Usar

### Requisição POST

```bash
curl -X POST http://localhost:5000/api/lgm/projeto-completo \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "um carro de corrida vermelho com detalhes metálicos",
    "include_analysis": true,
    "include_budget": true
  }'
```

### Resposta Completa

```json
{
  "success": true,
  "prompt": "um carro de corrida vermelho com detalhes metálicos",
  "timestamp": 1731274816.123,
  "stages": {
    "lgm_generation": {
      "success": true,
      "method": "replicate",
      "prompt": "um carro de corrida vermelho com detalhes metálicos",
      "output_files": ["/workspace/output/carro_racing.ply"],
      "processing_time": 15.4,
      "format": "gaussian_splat"
    },
    "project_analysis": {
      "success": true,
      "volume_estimado": 85.5,
      "materiais_recomendados": ["PLA+", "PETG"],
      "complexidade": "media",
      "tempo_estimado": "4-6 horas"
    },
    "budget_calculation": {
      "success": true,
      "volume_total": 85.5,
      "custos": {
        "material": 12.50,
        "impressao": 25.00,
        "total": 37.50
      },
      "filamentos_sugeridos": [...]
    }
  },
  "overall_status": "complete",
  "completion_rate": "3/3 estágios"
}
```

## 🎨 Endpoints LGM Individuais

### 1. Status do Sistema LGM

```bash
curl http://localhost:5000/api/lgm/status
```

### 2. Gerar Modelo 3D de Texto

```bash
curl -X POST http://localhost:5000/api/lgm/gerar-texto \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "um robô humanoide com olhos LED",
    "num_outputs": 1,
    "resolution": 800,
    "guidance_scale": 7.5
  }'
```

### 3. Gerar Modelo 3D de Imagem

```bash
curl -X POST http://localhost:5000/api/lgm/gerar-imagem \
  -F "imagem=@minha_imagem.jpg" \
  -F "prompt=O que você vê aqui em 3D" \
  -F "num_outputs=1" \
  -F "resolution=800"
```

### 4. Converter Arquivo

```bash
curl -X POST http://localhost:5000/api/lgm/convert \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/workspace/output/modelo.ply",
    "format": "obj",
    "quality": "high"
  }'
```

## 🔧 Configuração

### Variável de Ambiente Necessária

Para usar o LGM, configure sua chave da API Replicate:

```bash
export REPLICATE_API_TOKEN="sua_chave_aqui"
```

### Iniciar o Servidor

```bash
python3 servidor_integracao.py
```

## 📊 Status do Sistema

- **Sem Replicate API**: Sistema LGM indisponível, mas sistema tradicional funciona
- **Com Replicate API**: Sistema completo ativo (LGM + Tradicional)
- **GPU Local**: Se você tem GPU + modelo LGM local, será usado automaticamente

## 🎯 Vantagens do Endpoint Integrado

1. **Simplicidade**: Um endpoint para projeto completo
2. **Eficiência**: Executa tudo em sequência otimizada
3. **Robustez**: Se um estágio falhar, continua com os outros
4. **Transparência**: Mostra status de cada etapa
5. **Flexibilidade**: Pode ativar/desativar estágios conforme necessário

## 🚀 Fluxo de Trabalho

```
Texto do Usuário 
    ↓
1. Geração LGM (modelo 3D AI)
    ↓
2. Análise Tradicional (volume, materiais)
    ↓
3. Orçamento Completo (custos reais)
    ↓
Projeto Completo com Tudo!
```

## 📈 Casos de Uso

- **Designer**: "Preciso de um objeto 3D + orçamento rápido"
- **Prototipagem**: "Teste de conceito + análise de viabilidade"
- **Educacional**: "Demonstração de projeto 3D completo"
- **Empresarial**: "Apresentação de projeto com custos reais"
