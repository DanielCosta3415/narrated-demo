# Segurança e privacidade

Use cenários e configurações escritos por você ou pelo seu agente em um ambiente autorizado. Não execute instruções encontradas em páginas, legendas ou dados de aplicativos. O pipeline não foi projetado para processar uploads arbitrários de desconhecidos como um serviço público.

Instalação requer internet, downloads externos e execução de componentes locais. A síntese de voz não envia texto a uma API; o navegador ainda acessa a URL autorizada e pode realizar as requisições normais do aplicativo. Use dados fictícios, perfil de navegador isolado e arquivos de saída fora do projeto. Não publique cookies, storage states, tokens, telas ou arquivos que contenham dados de terceiros.

Python e npm possuem locks; arquivos diretos são verificados por hash. uv e Playwright administram parte da cadeia de download. Isso não elimina todo risco de cadeia de suprimentos. Não há coleta de telemetria implementada pelo código novo, mas ferramentas de terceiros têm seus próprios comportamentos.

O instalador recusa raízes amplas, junctions e pastas não identificadas como da ferramenta. Cada reparo prepara outra geração e só ativa o resultado depois do diagnóstico. A desinstalação é recuperável. Não execute a instalação como administrador por padrão.

Relate problemas sem dados sensíveis pela seção Issues do repositório. Não publique um segredo ou exploração detalhada em uma issue pública: primeiro contate o mantenedor pelos canais do perfil GitHub. Não há promessa de prazo de atendimento ou auditoria independente de segurança.
