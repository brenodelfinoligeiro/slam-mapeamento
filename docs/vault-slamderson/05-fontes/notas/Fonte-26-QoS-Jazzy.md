---
tipo: fonte
estado: texto_primario_consultado
acesso: 2026-11-07
fonte_id: 26
---
# ROS 2 Jazzy — Quality of Service settings

## Identificação

- Tipo: especificação oficial/convenção ROS ou documentação dos mantenedores, não artigo revisado por pares.
- Data de publicação: s.d.; documentação viva consultada em 2026-11-07, não artigo publicado em 2026.
- Versão/recorte: Jazzy.
- URL consultada: <https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html>.
- URL efetiva: <https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html>.
- Acesso: 2026-11-07T09:29:58.524893-03:00.

## Evidência e avaliação

> Transient local : the publisher becomes responsible for persisting samples for “late-joining” subscriptions.

A durabilidade transient-local permite persistir amostras para assinantes tardios.[26]

Seção verificável: procurar o trecho acima no texto preservado. A página não é paginada; não há número de página inventado.

## Aplicação na monografia

Explicar mapa/estado retidos e compatibilidade publisher/subscriber. QoS não substitui os leases monotônicos do árbitro nem autenticação.

**Evidência local inspecionada:** `src/navegacao/navegacao_autonoma`, relativa à raiz do workspace. A fonte externa explica o método/interface; a configuração local informa a escolha efetiva. Os resultados são os recibos do projeto, não o desempenho publicado por terceiros.

## Preservação e limites

Texto recuperado por HTTP e extraído sem scripts: [evidência local](../evidencias/software-26.txt). SHA-256 do UTF-8 extraído: `e5cfab9f881f94a7500554e00bf657b3cac708c7d6b318dcae87f4ae33b376ac`. Não é PDF, cópia integral do HTML nem snapshot imutável do repositório. Branches/portais podem mudar; a coleta datada e o hash delimitam o texto consultado. Cópia integral mantida somente localmente pela política de publicação.

## Relações

[[05-fontes/Software-e-monografia]] · [[03-decisoes/Arbitro-de-movimento]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[26] https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html — ROS 2 Jazzy — Quality of Service settings
