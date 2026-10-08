# Critérios de liberação

## Escopo

Distribuição Windows x64 do plugin, runtime local e pipeline de tutoriais PT-BR com Dora/Alex. Não é uma garantia de ausência de bugs nem uma certificação universal para todos os agentes e sistemas operacionais.

## Gate para 1.0.0

- Testes de distribuição e pipeline aprovados no commit exato.
- Instalação independente e teste fictício completo de ambas as vozes aprovados no commit exato.
- Recursos necessários contidos no plugin instalado, sem caminhos particulares ou checkout adicional.
- Dependências Python com versões/hashes e npm com lock/integrity; downloads diretos fixados por hash. Python gerenciado e Chromium ainda usam a cadeia de download de uv/Playwright: não alegar hash-lock completo dessa cadeia.
- Diagnóstico, reparo versionado, rollback verificado e desinstalação recuperável testados.
- Pacote apenas de arquivos rastreados, sem modelos, executáveis, credenciais ou dados do projeto original; SHA256SUMS e manifesto por arquivo.
- Revisão visual dos exemplos e confirmação humana de audição Dora/Alex, vinculadas aos hashes registrados em `VALIDATION.md`.
- Versão da integração testada e limites documentados. Publicação no diretório universal, assinatura Authenticode e outros sistemas são canais/compatibilidades separados, não condições ficticiamente concluídas.

Não promover a candidata se qualquer gate relevante falhar. Revisões de voz devem registrar o hash do vídeo aprovado; qualquer alteração posterior no vídeo invalida essa aprovação. Uma atualização de componentes requer novos testes.
