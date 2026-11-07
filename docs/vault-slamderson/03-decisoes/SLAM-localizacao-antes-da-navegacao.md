---
tipo: decisao
estado: implementado_em_simulacao
atualizado: 2026-11-06
---
# SLAM e localização antes da navegação

## Pedido do autor

Implementar localização com SLAM sobre a simulação existente; navegação fica para depois. Esse pedido não autoriza deploy, motores, UART real ou uma pilha Nav2 completa.

## Escolha técnica do recorte

Reutilizar SLAM Toolbox 2.8.5, com configuração/composição em `localizacao/mapeamento_slam`. Gerar LaserScan em `dispositivos/lidar_simulado` contra um cenário assimétrico de segmentos. Não construir outro algoritmo SLAM nem publicar um mapa ideal como se fosse aprendido.

`map -> odom` é do SLAM; `odom -> base_footprint` é do EKF; RSP mantém a descrição. A referência perfeita serve a geração de raios e testes/visualização, não é medição de localização. A origem gráfica do mundo coincide virtualmente com map, sem impor pose perfeita ao estimador.

## Modos e persistência

- Mapeamento usa o executável async do SLAM Toolbox.
- Localização usa o executável próprio de localização e exige os arquivos `.posegraph` e `.data` salvos.
- PGM/YAML são salvos para ocupação e futura integração; não substituem os arquivos do grafo no modo escolhido.
- Não iniciar AMCL e SLAM disputando TF. AMCL não foi implementado nesta etapa.
- Dados mutáveis ficam fora do share instalado; helper monta `/mapas` persistente e não sobrescreve prefixos existentes silenciosamente.

As interfaces são tipos upstream/padrão, sem pacote central ou cópias locais. Nome afetivo continua fora da identidade ROS.

## Limites

Mundo e LiDAR cinemáticos, sem contato/dinâmica, distorção de scanner rotativo ou calibração real do C1. Grafo foi recarregado no mesmo ambiente AMD64; compatibilidade de serialização entre arquiteturas/versões e transferência para a Pi exigem novo teste. A próxima etapa de navegação ainda não existe.

[Guia operacional](../../slam/LEIA-ME.md) · [[04-experimentos/SLAM-virtual-e-localizacao]] · [[03-decisoes/Arquitetura-atual]] · [[Inicio]]

## Fundamentação bibliográfica

[[05-fontes/Software-e-monografia|Roteiro para a monografia e distinção entre método e resultado]] · [[05-fontes/notas/Fonte-28-SLAM-Toolbox-Jazzy]] · [[05-fontes/notas/Fonte-29-REP-105]] · [[05-fontes/notas/Fonte-34-SLAM-Toolbox-2021]] · [[05-fontes/notas/Fonte-37-Revisao-SLAM2D-2025]]
