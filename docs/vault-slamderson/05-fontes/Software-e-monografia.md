---
tipo: mapa_bibliografico
projeto: robo_movel
atualizado: 2026-11-07
estado: fontes_consultadas_e_vinculadas
---
# Software e fundamentação para a monografia

## Escopo e como usar

Esta nota liga **fonte externa → método/interface → escolha implementada → evidência própria**. Não é a monografia pronta nem uma segunda arquitetura. A base é o recorte ROS 2 Jazzy consolidado no commit `5327c80`, conferido com os guias e configurações locais em 2026-11-07. Trabalhos concorrentes ainda não consolidados, inclusive interface web/API, não foram incorporados automaticamente como software demonstrado.

A coleta reúne **14 referências: seis trabalhos científicos e oito documentos oficiais/de mantenedores**. O núcleo recente é a revisão de 2025 e o artigo RPP de 2023. Os trabalhos de 2022, 2021, 2020 e 2016 permanecem porque fundamentam diretamente as ferramentas usadas; não foram rebatizados como recentes. Documentação Jazzy consultada agora complementa os artigos, mas **acesso em 2026 não significa publicação em 2026**.

Para escrever:

1. Use a revisão recente para situar o problema e os métodos alternativos.
2. Cite os trabalhos originais para os métodos/pacotes efetivamente utilizados.
3. Cite documentação da distribuição para interfaces e comportamento configurável.
4. Sustente desempenho e funcionamento do projeto exclusivamente pelos próprios ensaios e recibos, com seus limites.

## Leitura prioritária e papel de cada trabalho

### 1. Contexto recente: SLAM 2D LiDAR — Ran et al. (2025)

*A Review of 2D Lidar SLAM Research*, Remote Sensing, 17(7), 1214. DOI `10.3390/rs17071214`. Revisão diretamente pertinente ao recorte 2D, com comparação qualitativa de custo frente ao LiDAR 3D.[37]

- Usar em **introdução, revisão da literatura e justificativa do recorte 2D**.
- Não converter comparação qualitativa da revisão em orçamento medido deste protótipo.
- Discussões de visão, aprendizado profundo ou SLAM 3D não significam adoção dessas técnicas.
- [[05-fontes/notas/Fonte-37-Revisao-SLAM2D-2025|Ficha, PDF integral e limites]].

### 2. Seguimento de caminho: RPP — Macenski et al. (2023)

*Regulated pure pursuit for robot path tracking*, Autonomous Robots, 47(6), 685–694. DOI `10.1007/s10514-023-10097-6`. Apresenta heurísticas para regular a velocidade linear de uma variante de Pure Pursuit.[35]

- Usar em **fundamentação do controle de seguimento e escolha do controlador local**.
- É referência do RPP, não do planejador global ou do controle PI/PID das rodas.
- O YAML local desativa o lookahead escalado por velocidade; não descrever toda capacidade Adaptive do artigo como configuração ativa.
- [[05-fontes/notas/Fonte-35-RPP-2023|Ficha e resumo editorial consultado]].

### 3. Arquitetura: ROS 2 — Macenski et al. (2022)

*Robot Operating System 2: Design, architecture, and uses in the wild*, Science Robotics, 7(66), eabm6074. DOI `10.1126/scirobotics.abm6074`. Discute as mudanças arquiteturais e filosóficas do ROS 2.[32]

- Usar em **arquitetura de software, modularidade e integração distribuída**.
- Complementar com documentação Jazzy para interfaces concretas; esse artigo não documenta especificamente a distribuição escolhida.
- [[05-fontes/notas/Fonte-32-ROS2-2022|Ficha e distinção entre publicação e depósito arXiv]].

### 4. Mapeamento/localização: SLAM Toolbox — Macenski e Jambrecic (2021)

*SLAM Toolbox: SLAM for the dynamic world*, JOSS, 6(61), 2783. DOI `10.21105/joss.02783`. O artigo apresenta suporte a mapeamento e localização multissessão.[34]

- Usar em **SLAM por grafo e justificativa do pacote escolhido**.
- A recarga do grafo do projeto deve ser demonstrada pelo recibo local; capacidades multissessão disponíveis no pacote não são resultados automaticamente obtidos.
- [[05-fontes/notas/Fonte-34-SLAM-Toolbox-2021|Ficha e PDF integral]].

### 5. Navegação e BT: Nav2 — Macenski et al. (2020)

*The Marathon 2: A Navigation System*, IROS 2020, 2718–2725. DOI `10.1109/IROS45743.2020.9341207`. Fundamenta a orquestração de tarefas de navegação por árvore de comportamento.[33]

- Usar em **arquitetura de navegação e coordenação de planejamento/controle**.
- Artigo de congresso fundacional: não equivale ao manual atual do Nav2 Jazzy nem à comprovação da seleção NavFn/RPP.
- [[05-fontes/notas/Fonte-33-Nav2-Marathon-2020|Ficha e resumo do manuscrito]].

### 6. Fusão sensorial: robot_localization — Moore e Stouch (2016)

*A Generalized Extended Kalman Filter Implementation for the Robot Operating System*, capítulo em Intelligent Autonomous Systems 13, 335–348. DOI `10.1007/978-3-319-08338-4_25`. Apresenta o pacote robot_localization e sua implementação EKF.[36]

- Usar em **estimativa de estado e fusão sensorial**; completar com a configuração ROS 2 atual.
- Ano da referência editorial do capítulo: **2016**. O evento foi em 2014 e há datas online de 2015; são marcos distintos, detalhados na ficha.
- É fonte fundacional do pacote, não evidência de sua configuração ou precisão neste robô.
- [[05-fontes/notas/Fonte-36-EKF-Moore-Stouch-2016|Ficha e conflito de datas explicitado]].

## Mapa de aplicação na implementação

### ROS 2, comunicação e arbitragem

A documentação Jazzy distingue políticas QoS; transient-local preserva amostras para assinantes que chegam depois.[26]

- Evidência local: `src/navegacao/arbitro/` e `src/navegacao/navegacao_autonoma/`, relativos à raiz do workspace.
- Explicar tópicos, serviços, ações, carimbos, estado retido e escolha de QoS com referência à implementação, sem atribuir ao DDS todos os mecanismos próprios.
- **Contribuição própria:** seleção manual/autônoma, época de comandos, expiração e coordenação de cancelamento. QoS não prova E-stop, autenticação ou parada física.
- [[05-fontes/notas/Fonte-26-QoS-Jazzy]] · [[03-decisoes/Arbitro-de-movimento]] · [[04-experimentos/Arbitragem-manual-autonoma]].

### Modelo URDF, visualização e TF

Robot State Publisher recebe o modelo cinemático URDF; tf2 acompanha os referenciais no tempo.[30][31]

- Evidência local: `src/descricao/robo_movel/descricao/robo_movel.urdf` e [guia da descrição](../../descricao-ros/LEIA-ME.md).
- RSP/URDF fundamentam representação e transformações. RViz é visualização/inspeção; **não é simulador de dinâmica nem prova de colisão física**.
- Unidades/eixos já possuem referência REP 103 em [[05-fontes/Descricao-ROS]]; reaproveitar essa evidência, sem duplicar cadastro com numeração incompatível.
- [[05-fontes/notas/Fonte-30-RSP-Jazzy]] · [[05-fontes/notas/Fonte-31-TF2-Jazzy]] · [[04-experimentos/Descricao-ROS-R05]].

### Odometria das rodas e EKF planar

A configuração de robot_localization documenta o modo planar por `two_d_mode`.[27]

- Evidência local: `src/localizacao/odometria_rodas/` e `src/localizacao/fusao_sensores/configuracao/estimador.yaml`.
- Estado inspecionado: `two_d_mode: true`, velocidades X/Y da odometria e velocidade angular Z da IMU; não fusão de pose perfeita nem de orientação absoluta medida pela MPU-6050.
- A integração cinemática própria e a escolha de variáveis/covariâncias precisam ser descritas como implementação/configuração do projeto, não algoritmo novo proposto pelo artigo EKF.
- [[05-fontes/notas/Fonte-27-Configuracao-EKF]] · [[05-fontes/notas/Fonte-36-EKF-Moore-Stouch-2016]] · [[02-fundamentos/Contagem-e-odometria]] · [[04-experimentos/Simulacao-odometria-IMU-teleop]].

### SLAM, persistência e referenciais globais

SLAM Toolbox oferece localização sobre grafo de poses; a REP 105 distingue a utilidade local do referencial odométrico de sua deriva a longo prazo.[28][29]

- Evidência local: `src/localizacao/mapeamento_slam/configuracao/slam.yaml` e [guia SLAM](../../slam/LEIA-ME.md).
- No projeto: SLAM possui `map -> odom`; EKF possui `odom -> base_footprint`; RSP completa a árvore do modelo.
- Separar mapa de ocupação PGM/YAML de `.posegraph`/`.data`. Localização escolhida é sobre grafo; **AMCL não é o método implementado**.
- [[05-fontes/notas/Fonte-28-SLAM-Toolbox-Jazzy]] · [[05-fontes/notas/Fonte-29-REP-105]] · [[03-decisoes/SLAM-localizacao-antes-da-navegacao]] · [[04-experimentos/SLAM-virtual-e-localizacao]].

### Planejamento global e seguimento de caminho

NavFn permite Dijkstra ou A*, e RPP regula velocidade pelo caminho.[24][25]

- Evidência local: `src/navegacao/navegacao_autonoma/configuracao/nav2.yaml`.
- No YAML: `NavfnPlanner`, **`use_astar: false` → Dijkstra**, `allow_unknown: false`; controlador `RegulatedPurePursuitController`.
- Separar planejamento global, seguimento local, costmaps e arbitragem. O candidato DWB preservado não é o controlador vigente.
- [[05-fontes/notas/Fonte-24-NavFn-Jazzy]] · [[05-fontes/notas/Fonte-25-RPP-Jazzy]] · [[05-fontes/notas/Fonte-35-RPP-2023]] · [[03-decisoes/Navegacao-Nav2-arbitrada]] · [[04-experimentos/Navegacao-virtual-Nav2]].

## Roteiro sugerido para os capítulos

- **Introdução:** problema, objetivo, restrições de baixo custo e escopo 2D; revisão de 2025, sem prometer desempenho físico.
- **Fundamentação:** ROS 2/TF, cinemática e odometria, EKF, SLAM por grafo, planejamento em grade e RPP. Fontes dos métodos acima; equações devem receber referência específica antes da redação final.
- **Trabalhos relacionados:** revisão recente e métodos alternativos nela discutidos. Identificar quais comparações vêm da literatura e quais foram ensaiadas no projeto.
- **Metodologia e implementação:** pacotes, fluxos, configuração Jazzy, composição, parâmetros sintéticos, árvore TF, persistência e arbitragem. Explicitar o que é próprio e o que é dependência upstream.
- **Validação:** critérios de aceite, cenário, ruído sintético, ground truth só no oráculo/geração de raios, cancelamento e perdas de dados. Usar [simulação](../../simulacao/LEIA-ME.md), [SLAM](../../slam/LEIA-ME.md) e [Nav2](../../navegacao/LEIA-ME.md), com os respectivos recibos.
- **Resultados e discussão:** resultados digitais observados, comparação com metas próprias e limites de transferência para hardware. Não transplantar métricas dos artigos como se fossem medições do robô.
- **Conclusão:** contribuição demonstrada e pendências físicas reais: UART, firmware, driver C1, calibração, alimentação, contato/dinâmica e ensaio na plataforma alvo.

## Recência, cobertura e lacunas honestas

Esta é uma base inicial focada no software implementado, **não uma revisão sistemática/exaustiva até 2026**. A busca encontrou uma revisão pertinente de 2025; não houve necessidade de trocar trabalhos originais por um artigo de 2026 apenas pela data. Antes da redação final, ampliar a revisão experimental para comparação de métodos 2D e selecionar fonte específica para as equações cinemáticas e protocolo de avaliação que realmente serão usados.

O simulador atual é cinemático próprio: **não declarar Gazebo**. As medições são virtuais: não declarar MPU/C1/ESP/UART em operação física. Docker e Python são ferramentas de execução/implementação; não foram promovidos a métodos científicos nem receberam artigos decorativos nesta coleta. Referências futuras de firmware/drivers devem corresponder à implementação que vier a existir.

## Arquivos, auditoria e reprodução

- [Bibliografia única BibTeX](referencias.bib): chaves estáveis `source24` a `source37`, sem renumerar as anteriores. Base para BibLaTeX/ABNT, **não formatação ABNT certificada**.
- [Ledger de citações](citacoes.json): identificadores e trechos literais.
- [Manifesto de software](software-fontes.json): URLs solicitadas/efetivas, limites, hashes e âncoras locais.
- [Manifesto de PDFs](manifesto-arquivos.json): originais efetivamente obtidos, páginas e hashes. Texto extraído não é PDF original.
- [Auditoria documental](../00-organizacao/Validacao-bibliografia-software.md): resultado e escopo da verificação.

**Validador integral somente na cópia local completa:** ele exige textos, PDFs e demais referências retidas. No clone público, ausências inventariadas são intencionais; use o recorte estrutural publicado na política de publicação ou restaure os originais antes de executar este comando. Não confundir uma ausência declarada com hash conferido.

Executar a partir da raiz deste vault:

```bash
python 05-fontes/validar-software.py
```

O caminho legado do vault foi preservado por compatibilidade; títulos e textos novos usam somente a identidade genérica do robô. A etapa de pesquisa não alterou configuração global do Obsidian nem publicou automaticamente. A publicação bibliográfica posterior foi autorizada pelo autor e mantém textos integrais/originais somente locais, conforme a política do repositório. Código e documentação da API/interface web concorrentes não integram este recorte.

[[Inicio]] · [[05-fontes/Catalogo-de-fontes]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[24] https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn — Nav2 Jazzy — NavFn Planner
[25] https://docs.nav2.org/jazzy/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp — Nav2 Jazzy — Regulated Pure Pursuit
[26] https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html — ROS 2 Jazzy — Quality of Service settings
[27] https://raw.githubusercontent.com/cra-ros-pkg/robot_localization/ros2/doc/configuring_robot_localization.rst — robot_localization — Configuring robot_localization (branch ros2)
[28] https://raw.githubusercontent.com/SteveMacenski/slam_toolbox/jazzy/README.md — SLAM Toolbox — README (branch jazzy)
[29] https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0105.rst — REP 105 — Coordinate Frames for Mobile Platforms
[30] https://raw.githubusercontent.com/ros/robot_state_publisher/jazzy/README.md — robot_state_publisher — README (branch jazzy)
[31] https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Tf2.html — ROS 2 Jazzy — Tf2
[32] https://arxiv.org/abs/2211.07752 — Robot Operating System 2: Design, architecture, and uses in the wild
[33] https://arxiv.org/abs/2003.00368 — The Marathon 2: A Navigation System
[34] https://joss.theoj.org/papers/10.21105/joss.02783.pdf — SLAM Toolbox: SLAM for the dynamic world
[35] https://link.springer.com/article/10.1007/s10514-023-10097-6 — Regulated pure pursuit for robot path tracking
[36] https://link.springer.com/chapter/10.1007/978-3-319-08338-4_25 — A Generalized Extended Kalman Filter Implementation for the Robot Operating System
[37] https://mdpi-res.com/d_attachment/remotesensing/remotesensing-17-01214/article_deploy/remotesensing-17-01214.pdf — A Review of 2D Lidar SLAM Research
