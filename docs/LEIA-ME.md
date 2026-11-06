# Robô móvel — documentação acadêmica

Esta pasta é a **fonte central da documentação do projeto**. Os textos são escritos em português brasileiro. A árvore `src/` contém código, metadados e recursos de execução, sem manuais distribuídos entre os módulos.

## Leitura recomendada

**Imagens publicáveis do Nav2:** [trajeto observado e métricas digitais](navegacao/imagens/LEIA-ME.md), sem malhas/CAD. Capturas e artefatos privados continuam identificados na política de publicação.

**Navegação autônoma virtual:** [Nav2, arbitragem, objetivos e falhas](navegacao/LEIA-ME.md). NavFn + Regulated Pure Pursuit, costmaps e integração com SLAM/árbitro; objetivos e desvio exercitados, sem hardware.

**Árbitro de movimento:** [manual/autônomo, comandos e limites](arbitro/LEIA-ME.md). Pacote separado com seleção explícita, expiração e parada; não implementa Nav2.

**SLAM e localização global na simulação:** [guia de operação e limites](slam/LEIA-ME.md). SLAM Toolbox, LiDAR virtual, mapa aprendido, persistência e localização por grafo; este recorte não inicia Nav2; a integração está no guia de navegação acima. Hardware permanece pendente.

**Simulação com teleop e localização por odometria/IMU:** [guia e escopo](simulacao/LEIA-ME.md), [RViz real](simulacao/previa-simulacao.png). Pacotes organizados nos cinco agrupadores; execução virtual, sem UART/hardware/deploy.

**Identidade ROS genérica:** pacote `robo_movel`, workspace `robo_movel_ws`; [decisão e escopo](vault-slamderson/03-decisoes/Identidade-generica-ROS.md), [proposta de pacotes](planejamento/2026-11-06_070015-separacao-pacotes-ros-ptbr.md). Os recortes de simulação local e SLAM estão implementados; navegação Nav2 também foi integrada; comunicação com ESP e LiDAR real continuam pendentes.

**Descrição ROS 2 do modelo R05:** [URDF, launches, calibração e validação](descricao-ros/LEIA-ME.md), [captura real do RViz](descricao-ros/previa-rviz.png). 7 links, 2 juntas de rodas e 18 malhas em metros; build, 18 testes, TFs e visualização exercitados em contêiner ROS 2 Jazzy isolado. Não é controle do robô ou modelo dinâmico calibrado.

**Revisão mecânica R05 para ensaio:** [kit e validações](fixacao-r05/LEIA-ME.md), [ZIP só STL](fixacao-r05/slamderson-STL-Ender3V3SE-r05.zip) e [manual atualizado](fixacao-r05/slamderson-r05-montagem-e-seis-vistas.pdf). Insertos M3 de 5,68 mm, presilhas rígidas sem alargar PCB, sem porcas/velcro/cintas. São 28 modelos/44 impressos de montagem + cupom separado; PDF com 12 páginas de guia e 29 fichas de seis vistas (41 páginas). CAD/STL e fatiamento auditados, não montagem física. Imprimir cupom e medir interfaces antes do lote. R04 abaixo preservada como histórico.

**Manual anterior (R04, com porcas/velcro):** [R04 — montagem e seis vistas por peça](impressao-r04/slamderson-r04-montagem-e-seis-vistas.pdf). Dez páginas de instruções ilustradas, inventário e mapa de ferragens; depois 24 fichas, cada uma com as seis projeções do modelo na mesma página. Saia antes do piso e porcas antes de fechar os acessos; fixação física de chassi/C1 ainda condicionada à medição. ZIP e PDF anterior preservados.

**Vistas anteriores (três por peça):** [PDF R04 — três vistas por modelo](impressao-r04/slamderson-r04-24-pecas-tres-vistas.pdf), 24 páginas e 72 projeções ortográficas, sem repetir cópias. Derivado dos mesmos bytes do ZIP de STL entregue; orientação de impressão, não desenho cotado de fabricação.

**Impressão Ender-3 V3 SE:** [ZIP somente com STL R04](impressao-r04/slamderson-STL-Ender3V3SE-r04.zip), 24 modelos para 42 peças, quantidades no nome. Peças orientadas individualmente, maior eixo XY de 197 mm; não imprimir o conjunto todo na mesma mesa nem reescalar. Limite de entrega: volume/fatiamento conferidos, encaixe físico ainda depende do hardware real.

**Pesquisa e ideias:** [abrir o índice do vault Obsidian](vault-slamderson/Inicio.md). O [catálogo de fontes](vault-slamderson/05-fontes/Catalogo-de-fontes.md) reúne os originais disponíveis e as avaliações de confiabilidade.

**Modelos mecânicos:** [catálogo de modelos 3D](modelos-3d/catalogo.md), com arquivos de referência, licenças, prévias e validações. A correspondência às peças físicas ainda precisa ser conferida.

**Disposição mecânica:** [vistas 2D com quatro AA](disposicao-2d/LEIA-ME.md), com duas plantas, lateral e frontal; envelopes e suportes propostos, sem aprovação de fabricação.

**Estudo visual anterior:** [R03 com suporte compacto do C1](carcaca-r03/LEIA-ME.md), base de 62 × 62 mm, carcaça removível e Basike real. [R02 com a ponte larga](carcaca-r02/LEIA-ME.md) e [R01 aberto](montagem-3d/LEIA-ME.md) preservados como anteriores.

**Componente real recebido:** [powerbank Basike](vault-slamderson/01-componentes/Powerbank-Basike.md), 150 × 70 × 30 mm e 420 g indicados, corrigido na R02. A nota registra também o perfil USB-C de 5 V/3 A da etiqueta. Os arquivos 2D/R01 antigos conservam suas hipóteses históricas.

1. [Visão geral e situação do projeto](01-visao-geral.md).
2. [Arquitetura e fluxos de dados](02-arquitetura.md).
3. [Componentes, ligações e evidências](03-componentes-e-ligacoes.md).
4. [Comunicação UART](04-comunicacao-uart.md).
5. [Preparação do ambiente e desenvolvimento](05-desenvolvimento-e-execucao.md).
6. [Validação, ensaios e calibração](06-validacao-e-calibracao.md).
7. [Decisões e pendências](07-decisoes-e-pendencias.md).
8. [Responsabilidades das pastas](responsabilidades.md).
9. [Convenções de escrita e manutenção](convencoes.md).

## Publicação e referências locais

O repositório está destinado a <https://github.com/brenodelfinoligeiro/slam-mapeamento>. Consulte a [política de publicação](publicacao-git.md): alguns arquivos de referência são preservados apenas localmente por falta de autorização de redistribuição confirmada.

## Evidências e histórico

- [Histórico preservado](historico/LEIA-ME.md): documentação anterior, mantida como registro e não como instrução vigente.
- [Validação da centralização](validacao-centralizacao.md): resultados reais da reorganização e da revisão do acionamento.
- Acionamento atual: módulo L298N. Ligações funcionais e cuidados estão no [capítulo de componentes](03-componentes-e-ligacoes.md).

## Limite desta entrega

Existem doze pacotes ROS concretos nos cinco agrupadores, com descrição, planta/sensores virtuais, odometria/IMU, EKF, teleop, SLAM/localização por grafo e navegação Nav2 arbitrada. Build e fluxos DDS foram exercitados em contêiner Jazzy no Xeon; os guias de cada recorte distinguem seus resultados. Não há aquisição/acionamento dos dispositivos físicos, firmware ou UART implementados. Os ensaios virtuais não comprovam desempenho físico, funcionamento do C1 real ou movimento do robô.

A documentação deve evoluir com cada implementação. Informações desconhecidas permanecem marcadas como pendentes; resultados de ensaios não executados não devem ser apresentados como observados.
