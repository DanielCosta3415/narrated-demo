# Validação da beta — 08/10/2026

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

Nenhum áudio, dado de cliente, vídeo do GerenciAr, runtime ou credencial é incluído no Git. Os testes usam somente a fixture fictícia.
