---
tipo: fonte
estado: texto_primario_consultado
acesso: 2026-11-07
fonte_id: 24
---
# Nav2 Jazzy — NavFn Planner

## Identificação

- Tipo: especificação oficial/convenção ROS ou documentação dos mantenedores, não artigo revisado por pares.
- Data de publicação: s.d.; documentação viva consultada em 2026-11-07, não artigo publicado em 2026.
- Versão/recorte: Jazzy.
- URL consultada: <https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn/>.
- URL efetiva: <https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn/>.
- Acesso: 2026-11-07T09:29:57.610472-03:00.

## Evidência e avaliação

> The Navfn Planner plugin implements a wavefront Dijkstra or A* expanded holonomic planner.

O plugin admite expansão Dijkstra ou A*. No projeto, `use_astar: false` seleciona Dijkstra, não A*.[24]

Seção verificável: procurar o trecho acima no texto preservado. A página não é paginada; não há número de página inventado.

## Aplicação na monografia

Fundamentar o planejamento global realmente selecionado; cruzar `use_astar` e `allow_unknown` com o YAML, em vez de escrever que usamos A* por hábito.

**Evidência local inspecionada:** `src/navegacao/navegacao_autonoma/configuracao/nav2.yaml`, relativa à raiz do workspace. A fonte externa explica o método/interface; a configuração local informa a escolha efetiva. Os resultados são os recibos do projeto, não o desempenho publicado por terceiros.

## Preservação e limites

Texto recuperado por HTTP e extraído sem scripts: [evidência local](../evidencias/software-24.txt). SHA-256 do UTF-8 extraído: `a2443b07474e3d3f51c2cc45651cb5f155b2d4991f0e375e9ce80cf7ed8c5b91`. Não é PDF, cópia integral do HTML nem snapshot imutável do repositório. Branches/portais podem mudar; a coleta datada e o hash delimitam o texto consultado. Cópia integral mantida somente localmente pela política de publicação.

## Relações

[[05-fontes/Software-e-monografia]] · [[03-decisoes/Navegacao-Nav2-arbitrada]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[24] https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn — Nav2 Jazzy — NavFn Planner
