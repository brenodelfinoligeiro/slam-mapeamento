---
tipo: fonte
estado: texto_primario_consultado
acesso: 2026-11-07
fonte_id: 29
---
# REP 105 — Coordinate Frames for Mobile Platforms

## Identificação

- Tipo: especificação oficial/convenção ROS ou documentação dos mantenedores, não artigo revisado por pares.
- Data de publicação: 2010; convenção fundacional, não publicação recente.
- Versão/recorte: REP 105 (Active no texto consultado).
- URL consultada: <https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0105.rst>.
- URL efetiva: <https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0105.rst>.
- Acesso: 2026-11-07T09:29:57.619520-03:00.

## Evidência e avaliação

> The ``odom`` frame is useful as an accurate, short-term local reference, but drift makes it a poor frame for long-term reference.

O referencial odométrico é útil localmente, mas sofre deriva a longo prazo.[29]

Seção verificável: procurar o trecho acima no texto preservado. A página não é paginada; não há número de página inventado.

## Aplicação na monografia

Justificar `map -> odom -> base_footprint`; EKF e SLAM possuem arestas diferentes, de dono único.

**Evidência local inspecionada:** `src/localizacao/fusao_sensores/configuracao/estimador.yaml`, relativa à raiz do workspace. A fonte externa explica o método/interface; a configuração local informa a escolha efetiva. Os resultados são os recibos do projeto, não o desempenho publicado por terceiros.

## Preservação e limites

Texto recuperado por HTTP e extraído sem scripts: [evidência local](../evidencias/software-29.txt). SHA-256 do UTF-8 extraído: `6bca6ae2b392bbb8e95c283c672549b832c58128feaccc4d77b6bf65534f565e`. Não é PDF, cópia integral do HTML nem snapshot imutável do repositório. Branches/portais podem mudar; a coleta datada e o hash delimitam o texto consultado. Cópia integral mantida somente localmente pela política de publicação.

## Relações

[[05-fontes/Software-e-monografia]] · [[03-decisoes/SLAM-localizacao-antes-da-navegacao]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[29] https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0105.rst — REP 105 — Coordinate Frames for Mobile Platforms
