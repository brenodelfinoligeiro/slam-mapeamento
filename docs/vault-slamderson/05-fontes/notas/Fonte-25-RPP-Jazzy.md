---
tipo: fonte
estado: texto_primario_consultado
acesso: 2026-11-07
fonte_id: 25
---
# Nav2 Jazzy — Regulated Pure Pursuit

## Identificação

- Tipo: especificação oficial/convenção ROS ou documentação dos mantenedores, não artigo revisado por pares.
- Data de publicação: s.d.; documentação viva consultada em 2026-11-07, não artigo publicado em 2026.
- Versão/recorte: Jazzy.
- URL consultada: <https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp/>.
- URL efetiva: <https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp/>.
- Acesso: 2026-11-07T09:29:57.802452-03:00.

## Evidência e avaliação

> It regulates the linear velocities by curvature of the path to help reduce overshoot at high speeds around blind corners allowing operations to be much more safe.

O controlador regula velocidade linear pela curvatura do caminho.[25]

Seção verificável: procurar o trecho acima no texto preservado. A página não é paginada; não há número de página inventado.

## Aplicação na monografia

Relacionar seguimento de trajetória e regulação de velocidade aos parâmetros de RPP. A política local não certifica segurança física.

**Evidência local inspecionada:** `src/navegacao/navegacao_autonoma/configuracao/nav2.yaml`, relativa à raiz do workspace. A fonte externa explica o método/interface; a configuração local informa a escolha efetiva. Os resultados são os recibos do projeto, não o desempenho publicado por terceiros.

## Preservação e limites

Texto recuperado por HTTP e extraído sem scripts: [evidência local](../evidencias/software-25.txt). SHA-256 do UTF-8 extraído: `637def6f407df3f19e591b1ea03e723fb8a13645761003f8f583412b89d6698b`. Não é PDF, cópia integral do HTML nem snapshot imutável do repositório. Branches/portais podem mudar; a coleta datada e o hash delimitam o texto consultado. Cópia integral mantida somente localmente pela política de publicação.

## Relações

[[05-fontes/Software-e-monografia]] · [[04-experimentos/Navegacao-virtual-Nav2]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[25] https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp — Nav2 Jazzy — Regulated Pure Pursuit
