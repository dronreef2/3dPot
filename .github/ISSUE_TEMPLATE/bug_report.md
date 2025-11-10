---
name: 🐛 Bug Report
about: Reportar um problema ou erro no projeto 3dPot
title: '[BUG] '
labels: ['bug', 'help wanted']
assignees: ['dronreef2']
---

<!--
Obrigado por reportar um bug! 

Antes de enviar, por favor verifique:
- [ ] Se o problema já foi reportado
- [ ] Se você seguiu as instruções de troubleshooting na documentação
- [ ] Se você pode reproduzir o problema consistentemente

A informações neste template nos ajudam a resolver o problema mais rapidamente.
-->

## 🐛 Descrição do Bug

Descrição clara e concisa do problema. Exemplo: 
> ESP32 monitor não conecta ao WiFi mesmo com credenciais corretas.

## 🔄 Para Reproduzir

Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '....'
3. Veja erro

**Comportamento esperado:** Descrição do que deveria acontecer

**Comportamento atual:** Descrição do que está acontecendo

**Frequência:** Sempre/Ocasionalmente/Uma vez

## 🎯 Projeto Afetado

Qual projeto do ecossistema 3dPot está com problema?

- [ ] 🔍 Monitor de Filamento ESP32
- [ ] 🚀 EsteTransportadora Arduino  
- [ ] 🏭 Estação QC Raspberry Pi
- [ ] 🔗 Integração entre projetos
- [ ] 📚 Documentação
- [ ] 🧪 Testes automatizados
- [ ] 🎨 Interface web
- [ ] ⚙️ CI/CD Pipeline

## 🖥️ Ambiente/Hardware

**Dispositivo Principal:**
- [ ] ESP32 DevKit V1
- [ ] Arduino Uno/Nano
- [ ] Raspberry Pi 4
- [ ] Outro: ____________

**Configuração do Hardware:**
- Versão do firmware/software: ____________
- Módulos/libraries utilizadas: ____________
- Conexões realizadas: ____________
- Alimentação utilizada: ____________

**Software:**
- [ ] Arduino IDE versão: ____________
- [ ] PlatformIO versão: ____________
- [ ] Python versão: ____________
- [ ] Sistema Operacional: ____________

## 🖼️ Evidências

Se aplicável, adicione screenshots, vídeos ou logs que demonstrem o problema:

**FOTOS DO PROBLEMA:**
- Foto do hardware/circuito
- Screenshot da interface web
- Foto do erro no display/LCD
- Vídeo do comportamento inesperado

**LOGS DE ERRO:**
```
Cole aqui os logs relevantes...
```

## 🔍 Troubleshooting Já Tentado

- [ ] Verificou as conexões conforme o [Guia de Conexões](assets/screenshots/GUIA-CONEXOES.md)
- [ ] Testou com código mínimo/de exemplo
- [ ] Verificou alimentação e voltagem
- [ ] Testou em ambiente diferente
- [ ] Consultou a [documentação Getting Started](README.md)
- [ ] Verificou se biblioteca/firmware está atualizado
- [ ] Outro: ____________

## 💡 Contexto Adicional

Qualquer contexto adicional que possa nos ajudar a entender o problema:
- Comportamento funcionava antes? Quando parou?
- Que mudanças foram feitas recentemente?
- Há alguma intermitência ou padrão no erro?
- Ambiente de testes vs produção?

## 📊 Severidade

- [ ] 🔴 **Crítico**: Sistema completamente inoperante
- [ ] 🟠 **Alto**: Funcionalidade principal não funciona
- [ ] 🟡 **Médio**: Funcionalidade secundária com problemas
- [ ] 🟢 **Baixo**: Interface/bug visual ou melhoria menor

## 🔧 Informações de Debug

Se aplicável, cole aqui informações técnicas que possam ajudar:

```bash
# Exemplo de comandos para coletar informações do sistema
pio device list
python --version  
arduino-cli version
vcgencmd get_camera  # Para Raspberry Pi
```

## 📱 Outras Informações

- [ ] Este é o primeiro problema que você encontra com o 3dPot?
- [ ] Já tentou reinstalar/reconfigurar?
- [ ] Tem acesso a um multímetro/equipamentos de teste?
- [ ] Consegue testar com hardware alternativo?

---

**Obrigado por nos ajudar a melhorar o 3dPot!** 🚀

<!--
Dica: Use a label 'help wanted' se precisar de assistência com debugging.
Dica: Use a label 'good first issue' se for um problema simples para novos contribuidores.
-->