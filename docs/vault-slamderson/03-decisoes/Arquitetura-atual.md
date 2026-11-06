---
tipo: decisao
estado: confirmado_pelo_autor
atualizado: 2026-11-06
---
# Arquitetura atual

## Decisões informadas pelo autor

- Trabalho acadêmico com conteúdo próprio em português brasileiro.
- Documentação detalhada em `docs/`; pesquisa e ideias interligadas neste vault.
- Raspberry Pi 5 de 8 GB prevista para ROS 2.
- ESP responsável pelo controle PI das rodas e pela aquisição dos codificadores e da MPU-6050.
- Comunicação UART direta e bidirecional entre Raspberry e ESP; IMU e codificadores retornam no mesmo enlace.
- Módulo L298N escolhido para acionamento nesta etapa.
- Codificadores identificados pelo autor como `mh-sensor-series`.
- Chassi maker 2WD com duas rodas motoras e um rodízio; autor selecionou a foto B, de base com abertura circular. Medidas, espessura e furação exata ainda precisam de conferência física.
- LiDAR C1 incluído, ainda com integração por confirmar.
- O autor definiu quatro pilhas AA para esta etapa. O powerbank da Raspberry permanece separado; holder e química das AA ainda precisam ser conferidos. A disposição está no [estudo 2D](../../disposicao-2d/LEIA-ME.md), com posições e suportes explicitamente propostos.

Estas são decisões do projeto, não afirmações retiradas de um catálogo. Não consultar documentos históricos como se sobrepusessem decisões posteriores do autor.

## Arquivos de impressão

O autor informou Ender-3 V3 SE e restringiu a entrega a STL considerando o volume. O [pacote R04](../../impressao-r04/slamderson-STL-Ender3V3SE-r04.zip) contém somente 24 STL para 42 peças, quantidades nos nomes, sem guia/PDF/G-code. Saia dividida em duas e teto em quatro; maior eixo XY 197 mm. Esses 24 arquivos são byte a byte os mesmos ensaiados no OrcaSlicer 2.4.2 com o perfil SE de 220 × 220 × 250 mm. Não demonstra montagem física, rosca real C1, fixação dos encoders ou correspondência dos componentes reservados.

O autor pediu posteriormente um [PDF de três vistas de cada peça sem repetições](../../impressao-r04/slamderson-r04-24-pecas-tres-vistas.pdf). Entrega adicional: 24 páginas/24 modelos distintos/72 projeções ortográficas (superior, frontal, lateral direita), derivadas exatamente dos STL do ZIP anterior, que permaneceu inalterado. Não é um manual ou liberação de fabricação.

A solicitação posterior passou a incluir montagem e todas as vistas na mesma página. O [manual R04 atualizado](../../impressao-r04/slamderson-r04-montagem-e-seis-vistas.pdf) tem 10 páginas de instruções e 24 fichas com seis projeções cada (144 vistas), sem repetir cópias. As figuras usam o FCStd R04 reaberto e as fichas usam os mesmos STL entregues. Procedimento proposto: base e módulos inferiores, saia/clipes antes do piso, pré-módulo superior na bancada, piso, tetos e portas; carregar porcas antes de fechar acessos. C1, chassi real, holder, ESP, encoders e cabos continuam com pendências físicas explícitas.

## Mudança de fixação solicitada

O autor confirmou [[01-componentes/Insertos-e-retencoes|insertos M3 de 5,68 mm (Ø4,0 liso / Ø4,7 dentado)]] e presilhas rígidas pelas bordas, sem alargar PCB e sem porcas/velcro/cintas. A [R05](../../fixacao-r05/LEIA-ME.md) foi gerada e auditada: 28 modelos/44 peças de montagem, mais cupom P25; 68 parafusos/68 insertos/60 arruelas. Os 29 STL passaram no Orca; manual atualizado com 41 páginas. R04 permanece histórica. Ainda é protótipo dimensional: cupom, chassi/C1/ESP/holder reais e ensaios de carga/térmica pendentes. MPU mudou −12X/−3Y/+8Z, extrínseca a medir e refletir futuramente no ROS; L298N mudou −3Y/+4Z. Retirada do teto: elevar 2 mm antes de deslizar. Troca AA vertical auditada só com módulo superior desmontado; não presumir que a porta frontal resolva a troca.

## Descrição ROS derivada do modelo

Por solicitação do autor, a R05 agora fornece URDF, 18 malhas em metros e launches de descrição/visualização. [Detalhes e validação](../../descricao-ros/LEIA-ME.md). As rodas são juntas contínuas; `lidar_mount_link`/`imu_mount_link` são datums de montagem, não frames calibrados dos dados. Não há inércias ou limites de acionamento fictícios.

Build, 16 testes e TFs foram executados em ROS 2 Jazzy isolado e o modelo foi inspecionado em RViz real. Isso não implanta ROS na Pi nem implementa comunicação com dispositivos. O rodízio da referência fica 5,313 mm acima do plano das rodas; a geometria foi mantida e a pendência registrada, não mascarada no URDF.

## Limites preservados

O autor fechou a quantidade em quatro AA. O [[01-componentes/Powerbank-Basike|powerbank real Basike]] tem envelope informado de 150 × 70 × 30 mm e massa indicada de 420 g; a etiqueta fotografada informa saída USB-C de 5 V/3 A e total de 15 W. Química das AA, holder, alimentação do ESP, retenção mecânica, capacidade efetivamente entregue/autonomia e funcionamento sob carga permanecem pendentes. O exemplar não fornece o perfil USB-C de 5 V/5 A recomendado para a Pi 5; compatibilidade sob a carga planejada precisa ser ensaiada.[23]

O autor informa que os motores são de 12 V; essa especificação ainda precisa ser conferida na etiqueta/datasheet do modelo exato. A escolha posterior de quatro AA substitui o exemplo de oito alcalinas discutido anteriormente. Quatro alcalinas em série correspondem a 6 V nominais (NiMH: 4,8 V), antes da queda da L298N. Partida, torque e desempenho com essa alimentação não foram validados; não foi adotado conversor elevador nem substituído o driver.

Placa ESP final, bateria dos motores, GPIOs, taxa/protocolo UART, revisão exata dos módulos dos sensores, geometria, correntes dos motores e distribuição ROS 2 permanecem pendentes.

O autor solicitou corrigir o 3D e manter a eletrônica coberta; depois rejeitou a largura/aparência do suporte do LiDAR. A proposta atual é a [R03 com suporte C1 compacto](../../carcaca-r03/LEIA-ME.md): base de 62 × 62 × 3 mm em vez de 130 mm de largura, apoios internos, Basike real embaixo atrás, ESP no segundo piso, seis peças de carcaça ventilada e C1 exposto acima do teto. Dimensões do suporte, paredes, fixadores e folgas são propostas geométricas, não montagem física aprovada. A R02, R01 e prancha 2D foram preservadas como anteriores. Veja [[01-componentes/Suporte-C1|o suporte e suas pendências]].

O software atual tem doze pacotes com descrição, sensores cinemáticos, odo/IMU/EKF, teleop e SLAM/localização por grafo. Esses fluxos foram exercitados em ROS/DDS real no contêiner Jazzy, sem nós de hardware. Teste virtual não valida movimento físico, UART, IMU ou C1 reais.

## Ligações conceituais

Referência de velocidade -> ESP -> direção/PWM -> L298N -> motores.
Codificadores e IMU -> ESP -> UART -> Raspberry -> odometria/localização.
LiDAR -> interface ainda a confirmar -> Raspberry -> mapeamento/navegação.

[[01-componentes/Encoder-MH-Sensor-Series]] · [[01-componentes/L298N]] · [[01-componentes/MPU-6050]] · [[06-ideias/Ideias-e-pendencias]]

## Sources

[23] https://pip.raspberrypi.com/documents/RP-009856-WP — Raspberry Pi Ltd — USB Power Delivery on Raspberry Pi 5

## Identidade do software ROS

[[03-decisoes/Identidade-generica-ROS]]: pacote atual `robo_movel`, workspace `robo_movel_ws`; organização-alvo somente em `descricao`, `localizacao`, `dispositivos`, `navegacao` e `percepcao`, com pacotes específicos internos e sem manifestos nos agrupadores. SLAM/mapeamento está em `localizacao`; comando de rodas em `navegacao`. A migração dos agrupadores foi concluída no recorte de simulação, sem implantação em hardware; navegação Nav2 foi integrada na simulação; funcionalidades físicas continuam pendentes.

## Simulação funcional

[[04-experimentos/Simulacao-odometria-IMU-teleop]]: recorte com sensores virtuais e teleop exercitado no Xeon, sem hardware.

## SLAM e localização implementados no recorte virtual

[[03-decisoes/SLAM-localizacao-antes-da-navegacao]] registra a prioridade escolhida pelo autor e o recorte técnico. [[04-experimentos/SLAM-virtual-e-localizacao]] separa execução DDS/mapeamento/recarga de qualquer ensaio físico. O SLAM assume somente `map -> odom`; EKF mantém a odometria local.

## Árbitro de movimento

[[03-decisoes/Arbitro-de-movimento]] registra o pacote separado solicitado pelo autor, sem antecipar a implementação de Nav2.

## Navegação Nav2 integrada

[[03-decisoes/Navegacao-Nav2-arbitrada]]: NavFn + RPP + costmaps + proteção de entradas/objetivos antes do árbitro. [[04-experimentos/Navegacao-virtual-Nav2]] registra os ensaios sem hardware.
