---
tipo: experimento
estado: executado_digitalmente
atualizado: 2026-11-06
---
# SLAM virtual e localização por grafo

## Executado

Build/instalação dos dez pacotes e integração ROS/DDS em contêiner Jazzy isolado no Xeon. O LiDAR virtual publica raios carimbados a partir de referência perfeita e extrínseca fixa; o SLAM não assina essa referência. Seu mapa é comparado independentemente às paredes conhecidas do cenário.

Um percurso de ensaio percorre um retângulo livre por comandos de velocidade com tempo simulado. Isso não é planejamento ou navegação autônoma. Foram verificados mapa não trivial, pose global, lifecycle ativo, autoria causal de `map -> odom` e continuidade da odometria EKF durante pausa somente do processo SLAM.

O utilitário real salva ocupação PGM/YAML e grafo/data; arquivos efetivos/tamanhos/hashes são conferidos, não apenas respostas de serviço. Uma nova composição inicia o executável de localização e carrega o mesmo grafo, mantendo os arquivos originais inalterados. Ausência de grafo/serviço, modo inválido, prefixo já existente e parâmetro inválido de sensor têm ensaios negativos.

## Visualização

RViz real usa frame map, LaserScan, mapa, robô e trajetórias. A composição isola o include da base em GroupAction: seu `rviz:=false` não pode apagar a escolha do RViz SLAM no contexto pai. Um teste executa o motor launch real para esse vazamento de configuração.

O RViz pode abrir modal de configuração alterada ao fechar; o ensaio confirma salvamento só da cópia instalada no contêiner/Xvfb privado, antes de SIGINT do launch. Isso não altera a fonte e não deve ser confundido com salvar o mapa de SLAM.

## Interpretação

É verificação de integração/algoritmo num mundo sintético. Resolução de grade não é precisão física; valores de erro muito pequenos neste cenário idealizado não especificam desempenho no robô. Não houve calibração, contato, hardware, navegação, impressão ou deploy. Inicialização coincide com a origem conhecida do cenário; não é ensaio de localização global arbitrária ou recuperação de robô sequestrado.

[Operação, relatórios e limitações](../../slam/LEIA-ME.md) · [[03-decisoes/SLAM-localizacao-antes-da-navegacao]] · [[04-experimentos/Simulacao-odometria-IMU-teleop]] · [[Inicio]]

## Endurecimento da persistência e do encerramento

A validação da exportação encontrou timeout no proxy que cria outro comando para salvar ocupação. O recorte passou a usar servidor nativo persistente `salvador_mapa`, mantendo 2 s como prazo interno e QoS transient-local. A causa exata de descoberta/agendamento do proxy não foi isolada. Grafo continua pelo serviço do SLAM; ocupação pelo serviço nav2_msgs/SaveMap, cujo result é bool e não enum zero. Há exigência de três gravações consecutivas.

Uma falha de SDK em take_message no SIGINT do nó diagnóstico de trajetórias ganhou tratamento estreito condicionado ao contexto inválido, com regressão que preserva a propagação de erro em contexto válido e de outros erros.
