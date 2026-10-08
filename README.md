# Narrated Demo

Tutoriais de software com gravação Cutaway, cursor visível, narração local em português com Dora ou Alex e saída 1080p/60 FPS. A integração com Codex auxilia na elaboração do roteiro e na revisão das evidências; não exige chave de uma API de síntese.

## Estado da distribuição

Beta para Windows x64. Não é uma versão estável nem um plugin listado no diretório público do Codex. O histórico de verificações fica em `docs/VALIDATION.md`.

## Instalação

Baixe o código, extraia e execute `Install.cmd`. O instalador solicita confirmação, baixa dependências em uma pasta própria e não altera o PATH global. Requer internet, espaço para Chromium/modelos e autorização para executar os componentes. Downloads podem levar vários minutos.

A instalação automática não elimina as permissões do ambiente, a necessidade de acesso ao aplicativo demonstrado ou a revisão humana do vídeo. Não envie dados reais de clientes para os exemplos.

Para instalar a integração em uma versão do Codex que suporte plugins:

```powershell
codex plugin marketplace add DanielCosta3415/narrated-demo
codex plugin add narrated-demo@narrated-demo
```

Abra um novo chat e peça a configuração do Narrated Demo. O agente deve obter sua autorização antes de baixar e instalar o runtime. Caso sua versão não suporte plugins, a pasta da skill também pode ser instalada manualmente; outros agentes precisam suportar o formato SKILL.md e a execução local. Não há promessa de compatibilidade universal.

## Uso com Codex

A skill está em `plugins/narrated-demo/skills/narrated-demo`. Solicite um tutorial informando a URL local, o escopo e a voz desejada. O agente prepara os arquivos de captura e roteiro conforme os contratos da skill. O runtime isolado fica em `%LOCALAPPDATA%/NarratedDemo/runtime`.

Após instalar, o agente pode executar o `pipeline.py` com o Python do runtime e preencher os caminhos a partir de `runtime.json`. As validações técnicas não substituem a audição e a revisão visual. Não há publicação automática dos vídeos.

Para repetir o teste local, no checkout extraído:

```powershell
& "$env:LOCALAPPDATA/NarratedDemo/runtime/venv/Scripts/python.exe" tests/self_test.py "$env:LOCALAPPDATA/NarratedDemo/runtime/runtime.json" "$env:LOCALAPPDATA/NarratedDemo/self-test"
```

Para atualizar o código, use um novo checkout e mantenha os vídeos separados. Execute novamente o instalador para conferir as dependências. Esta beta não possui atualizador ou desinstalador automático: desative o plugin com o comando de remoção do Codex e preserve seus vídeos antes de remover a pasta própria do runtime.

## Licenças

Código novo: MIT. Cutaway mantém sua licença MIT. Modelos, vozes, Chromium, FFmpeg e bibliotecas têm termos próprios; consulte `THIRD_PARTY.md`. Não são distribuídos executáveis nem pesos neste repositório.
