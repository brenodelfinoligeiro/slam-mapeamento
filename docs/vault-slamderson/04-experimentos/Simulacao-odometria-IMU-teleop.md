# Simulação com odometria, IMU e teleop

## Escopo observado

Execução cinemática ROS 2 Jazzy no Xeon, em contêiner sem rede/dispositivos. Encoders e IMU virtuais, EKF robot_localization, teclado por PTY e RViz real. Não é Gazebo, calibração física ou teste do ESP. PID e firmware reais continuam pendentes.

A descrição foi movida sem alterar seus bytes de URDF/malhas. Existem somente cinco agrupadores sem manifesto: descricao, localizacao, dispositivos, navegacao e percepcao. O simulador é dono da mensagem LeituraRodas; consumidores importam esse contrato, sem pacote central de interfaces.

## Evidências

[Guia, fluxos e limitações](../../simulacao/LEIA-ME.md), [captura RViz](../../simulacao/previa-simulacao.png). Relatório e logs ficam em `docs/simulacao/`; dados numéricos são produzidos pelas execuções, não por estimativa textual.

## Interpretação

O cenário injeta escalas diferentes nos encoders e bias/ruído virtual na IMU. O tratamento remove o bias configurado; EKF usa velocidades das rodas e giroscópio, sem pose perfeita. Referência azul serve apenas como oráculo. Melhora no cenário não prevê precisão física; posição/rumo globais continuam sem observação absoluta.

Foram exercitados avanço/giro/ré, curva, fim de entrada, comandos inválidos, retorno à origem em reinício completo e encerramento normal. Pausa intencional do processo EKF confirma a origem da TF local sem suspender o RSP.

Relacionados: [[03-decisoes/Identidade-generica-ROS]], [[03-decisoes/Arquitetura-atual]], [[Inicio]].

## Extensão posterior

[[04-experimentos/SLAM-virtual-e-localizacao]] acrescenta observação laser e mapa global na composição própria; a limitação de ausência de observação global acima permanece válida para o launch local original, não para a composição SLAM.

## Fundamentação bibliográfica

[[05-fontes/Software-e-monografia|Roteiro para a monografia e distinção entre método e resultado]] · [[05-fontes/notas/Fonte-27-Configuracao-EKF]] · [[05-fontes/notas/Fonte-31-TF2-Jazzy]] · [[05-fontes/notas/Fonte-36-EKF-Moore-Stouch-2016]]
