# Narrated Demo

Tutoriais de software com gravação Cutaway, cursor visível, narração local em português com Dora ou Alex e saída 1080p/60 FPS. A integração com Codex auxilia na elaboração do roteiro e na revisão das evidências; não exige chave de uma API de síntese.

## Estado da distribuição

Candidata 1.0.0 para Windows x64. A promoção para estável depende dos critérios em `docs/RELEASE.md`, incluindo aprovação humana dos exemplos de voz. Não é um plugin listado no diretório público do Codex. O histórico de verificações fica em `docs/VALIDATION.md`.

## Instalação

Baixe o código, extraia e execute `Install.cmd`. O instalador solicita confirmação, baixa dependências em uma pasta própria e não altera o PATH global. Requer internet, espaço para Chromium/modelos e autorização para executar os componentes. Downloads podem levar vários minutos.

A instalação automática não elimina as permissões do ambiente, a necessidade de acesso ao aplicativo demonstrado ou a revisão humana do vídeo. Não envie dados reais de clientes para os exemplos.

Para instalar a integração em uma versão do Codex que suporte plugins:

```powershell
codex plugin marketplace add DanielCosta3415/narrated-demo --ref v1.0.0-rc.1
codex plugin add narrated-demo@narrated-demo
```

Abra um novo chat e peça a configuração do Narrated Demo. O agente deve obter sua autorização antes de baixar e instalar o runtime. Caso sua versão não suporte plugins, a pasta da skill também pode ser instalada manualmente; outros agentes precisam suportar o formato SKILL.md e a execução local. Não há promessa de compatibilidade universal.

## Uso com Codex

A skill está em `plugins/narrated-demo/skills/narrated-demo`. Solicite um tutorial informando a URL local, o escopo e a voz desejada. O agente prepara os arquivos de captura e roteiro conforme os contratos da skill. O runtime isolado fica em `%LOCALAPPDATA%/NarratedDemo/runtime`.

Após instalar, o agente pode executar o `pipeline.py` com o Python do runtime e preencher os caminhos a partir de `runtime.json`. As validações técnicas não substituem a audição e a revisão visual. Não há publicação automática dos vídeos.

Para repetir o teste local, no checkout extraído:

```powershell
$runtimeFile = "$env:LOCALAPPDATA/NarratedDemo/runtime/runtime.json"
$runtime = Get-Content -LiteralPath $runtimeFile -Raw | ConvertFrom-Json
& $runtime.python tests/self_test.py $runtimeFile "$env:LOCALAPPDATA/NarratedDemo/self-test"
```

O plugin inclui instalador, diagnóstico e teste: a configuração pelo Codex não precisa de outro clone. Para atualizar, instale a versão escolhida do plugin e execute seu setup. O instalador prepara uma geração nova; só ativa a configuração após o diagnóstico. A geração anterior permanece intacta. Reexecutar o instalador repara as dependências em outra geração, não sobrescreve o ambiente em uso.

Manutenção (sempre confirme o destino antes de executar):

```powershell
./installer/Maintain.ps1 -Action Rollback -ConfirmAction
./installer/Maintain.ps1 -Action Uninstall -ConfirmAction
```

O rollback verifica a geração anterior antes de ativá-la. A desinstalação renomeia a pasta própria para um arquivo recuperável, preservando todos os seus arquivos; remova/desative o plugin separadamente no Codex. Não há exclusão automática nem limpeza das gerações antigas. Na migração da beta sem marcador, mantenha aquela pasta intacta e escolha um novo destino vazio; não force adoção de diretórios.

Windows 11 x64 local e Windows Server x64 em runner independente são os ambientes de teste. macOS, Linux e ARM não fazem parte desta distribuição. Use pasta local, não UNC/junction. Sem assinatura Authenticode: o Windows pode solicitar confirmação. Verifique os hashes do pacote; eles comprovam integridade, não substituem uma assinatura de identidade.

## Licenças

Código novo: MIT. Cutaway mantém sua licença MIT. Modelos, vozes, Chromium, FFmpeg e bibliotecas têm termos próprios; consulte `THIRD_PARTY.md`. Não são distribuídos executáveis nem pesos neste repositório.
