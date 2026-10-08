# Validação da beta — 08/10/2026

## Candidata 1.0.0-rc.1

Verificado localmente em 08/10/2026:

- 8 testes de distribuição e 9 de pipeline aprovados; as duas skills passaram no validador formal.
- Instalador com locks, checksums, marcador de propriedade, proteção de ZIP e configuração por geração executado em diretório isolado. Falha de MAX_PATH do Expand-Archive encontrada e corrigida com extração por caminhos estendidos.
- Teste completo de captura, Dora/Alex, renderização, retomada e decodificação aprovado com FFmpeg/FFprobe 9.0.2, inclusive saída com espaços, acentos e apóstrofo.
- Diagnóstico executado da cópia realmente instalada do plugin `1.0.0-rc.1` no cache do Codex; todos os recursos necessários estavam presentes, sem checkout adicional.
- Quatro quadros amostrados (preparação e resultado de cada voz) inspecionados: cursor e formulário legíveis, legendas iniciais legíveis e resultado fictício visível.
- Dora: SHA256 `d2d71be7e58a92128d0d6890bf5067826a64c52728b2b6b92f8bbfe797416b3e`, −16,85 LUFS / −1,46 dBTP.
- Alex: SHA256 `b484c24a5746faf979b2d139e60bc5a98a0461988c9c2a4f9d78235739f5878e`, −16,96 LUFS / −1,46 dBTP.

A beta anterior passou no runner independente: https://github.com/DanielCosta3415/narrated-demo/actions/runs/37729616933 . Esse resultado não aprova automaticamente o novo commit candidato. Consulte a execução do workflow no commit da candidata; ele também testa reparo em outra geração e rollback real.

O commit da candidata passou no runner independente: https://github.com/DanielCosta3415/narrated-demo/actions/runs/37731418203 . Isso não aprova automaticamente alterações posteriores.

Em 08/10/2026 foi registrado o retorno humano: ambos os exemplos acima estão claros e sem cortes, com uma ressalva no encerramento da Dora (“Obrigado” deveria ser “Obrigada”). O exemplo do Alex foi preservado com o mesmo hash. A Dora foi regenerada com narração e legendas corrigidas, SHA256 `e6cc0ca04c0ac9bd3523fa7b9e52d833a83bf1d9855910d9654f327fc077cec9`: decodificação completa, 1920×1080, 60 FPS e retomada passaram; loudness decodificado −16,85 LUFS / −1,41 dBTP. Um quadro do encerramento foi inspecionado e mostra “Obrigada”, cursor e resultado legíveis. Nove testes de distribuição passaram, incluindo concordância por narrador.

O usuário confirmou posteriormente o encerramento corrigido da Dora (“Agora sim”), aprovando o arquivo regenerado identificado acima. Alex permanece aprovado com seu hash original. O commit de correção passou no runner independente: https://github.com/DanielCosta3415/narrated-demo/actions/runs/37732485192 . A publicação estável exige também sucesso do workflow no commit que define a versão 1.0.0; o resultado deve ser consultado nesse commit. As aprovações humanas estão registradas aqui, separadas da QA automática. A inspeção visual de quadros foi amostral, não integral; não há alegação de revisão contínua pelo agente.

Os limites de plataforma, assinatura e cadeia de download estão em `RELEASE.md` e `SECURITY.md`. A seção histórica abaixo descreve apenas a beta e seus componentes antigos.

## Verificado localmente

- Instalação em diretório isolado no Windows x64 existente, sem depender do Python/Node global para o pipeline.
- Python 3.12.10 gerenciado por uv 0.8.22; Node 24.11.0; Playwright 1.63.0, Chromium 153.0.8010.12.
- Checksums dos arquivos uv, Node, modelo ONNX e vetores de voz conferidos pelo instalador.
- Codex CLI 0.162.0-alpha.2 registrou o marketplace local e listou o plugin como instalado e habilitado.
- Oito testes unitários passaram. A execução inicial no sandbox falhou na limpeza do diretório temporário; a repetição autorizada passou.
- Teste fictício com captura real, síntese Dora e Alex e renderização: ambos passaram em decodificação completa, 1920×1080, 60 FPS, cadência, sincronização temporal, áudio e legendas.
- Reexecução preservou hashes e timestamps dos estágios reutilizáveis. Modelo ausente e temporização inválida foram rejeitados.
- Loudness decodificado: Dora −16,85 LUFS / −1,42 dBTP; Alex −16,93 LUFS / −1,49 dBTP.
- Quadro de resultado da Dora inspecionado: formulário legível, dado fictício, resultado e cursor visível.

## Limitações e pendências

- Não foi realizada audição contínua nem revisão visual integral dos dois vídeos; a QA mantém essas categorias como não verificadas.
- Teste local isolado não equivale a instalação em máquina independente. Workflow Windows foi preparado, mas seu resultado remoto deve ser consultado antes de alegar sucesso.
- Não foi verificada descoberta visual na interface do aplicativo Codex; o teste da integração foi pelo CLI.
- Não há certificação para macOS, Linux, Windows ARM ou outros agentes.
- Beta sem atualizador/desinstalador automático, assinatura de executável ou listagem no diretório público de plugins.
- Dependências Python estão fixadas por versão; a cadeia transitiva npm e o download gerenciado do Python não possuem lock de hashes completo nesta beta.
- As licenças de terceiros foram preservadas/documentadas; isso não constitui parecer jurídico sobre vozes/dados de treinamento.

Nenhum áudio, dado de cliente, vídeo do projeto de origem, runtime ou credencial é incluído no Git. Os testes usam somente a fixture fictícia.
