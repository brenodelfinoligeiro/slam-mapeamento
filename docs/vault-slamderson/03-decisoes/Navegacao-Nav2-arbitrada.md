# Navegação Nav2 arbitrada

## Decisão e escopo

O autor solicitou integrar navegação autônoma ao SLAM e ao árbitro existentes. Implementação digital no pacote `navegacao/navegacao_autonoma`, sem sexto agrupador, firmware, deployment, commit ou push.

NavFn planeja sobre mapa aprendido e scan; Regulated Pure Pursuit segue o caminho com costmap local. A entrada no árbitro é TwistStamped via proteção de autonomia, não disputa direta de /cmd_vel. EKF mantém odom->base_footprint; SLAM mantém map->odom. Ground truth somente gera raios e avalia o ensaio.

O candidato DWB foi preservado após mínimos de custos e progresso insuficiente; RPP foi escolhido pela ausência desse mecanismo discreto e pelo resultado real dos mesmos objetivos, sem afrouxar o oráculo de colisão ou watchdogs.

## Autoridade e pré-requisitos

Padrão manual. Seleção abre época; o cancelamento preventivo precisa receber ACK antes de aceitar objetivo novo. Tomada manual/parada cancela objetivos, sem retomá-los automaticamente ao retornar ao autônomo. Sensor recuperado não rearma falha. Perda de scan/odom/TF/clock durante objetivo ativo trava parada. Falta de velocidade só neutraliza, pois pode haver planejamento em andamento.

Associação entre velocidade e objetivo é temporal: TwistStamped não contém UUID. Não é autenticação ROS ou E-stop certificado. PI/PID e proteção elétrica permanecem no ESP/camada física futura. RPP regula velocidade; não se declara rampa linear física calibrada.

Lifecycle SLAM/salvador tem dono nativo único; lifecycle Nav2 só inicia após mapa, sensores e TF prontos. Os launches legados foram preservados; usar a composição nova explicitamente.

[Guia e parâmetros](../../navegacao/LEIA-ME.md) · [[03-decisoes/Arbitro-de-movimento]] · [[03-decisoes/SLAM-localizacao-antes-da-navegacao]] · [[04-experimentos/Navegacao-virtual-Nav2]] · [[Inicio]]

## Fundamentação bibliográfica

[[05-fontes/Software-e-monografia|Roteiro para a monografia e distinção entre método e resultado]] · [[05-fontes/notas/Fonte-24-NavFn-Jazzy]] · [[05-fontes/notas/Fonte-25-RPP-Jazzy]] · [[05-fontes/notas/Fonte-29-REP-105]] · [[05-fontes/notas/Fonte-33-Nav2-Marathon-2020]] · [[05-fontes/notas/Fonte-35-RPP-2023]]
