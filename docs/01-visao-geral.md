# 1. Visão geral

## Finalidade

Este é um trabalho acadêmico de robótica móvel baseado em um carrinho de tração diferencial. O projeto pretende integrar acionamento das rodas, odometria, medição inercial e LiDAR para estudar localização, construção de mapas e navegação.

A implementação será incremental: primeiro aquisição e controle básico, depois estimativa de movimento, mapeamento e navegação. A presença de uma pasta não significa que a funcionalidade correspondente já existe.

## Plataforma informada

- Raspberry Pi 5 com 8 GB como computador embarcado do ROS 2.
- Desenvolvimento da estrutura de software realizado no Xeon.
- ESP para leitura dos codificadores e da MPU-6050, controle das rodas e comunicação UART.
- Dois motorredutores amarelos da família TT e discos ópticos.
- IMU MPU-6050.
- LiDAR C1 incluído pelo autor; ligação e controlador ainda a confirmar.
- Módulo de ponte H dupla L298N para acionamento dos dois motores.

O ESP32-C3 SuperMini foi considerado, mas a escolha final da placa não foi confirmada. Para a L298N, a proposta usa saídas de direção e PWM comum, disponível por LEDC; MCPWM não é requisito. O ESP32 clássico continua sendo uma opção por seu contador de pulsos PCNT, enquanto o C3 pode contar pulsos por interrupções.

## O que existe no software

Há doze pacotes específicos nos agrupadores `descricao`, `localizacao`, `dispositivos`, `navegacao` e `percepcao`. A descrição R05 é reutilizada pela simulação de encoders/IMU, EKF e teleop; LiDAR virtual e SLAM Toolbox produzem mapa e localização global. A composição e utilitário de persistência têm executáveis/launches reais. Aquisição, controle e calibrações de hardware permanecem pendentes.

Build, testes, RSP/TF e RViz foram exercitados em contêiner ROS 2 Jazzy isolado. Não foi instalado ROS nativo no host nem escolhida a distribuição final da Pi. Esse ensaio não comprova comunicação com hardware.

## Escopo proporcional

Trata-se de um protótipo didático pequeno, não de um robô industrial. Manter cuidados elétricos básicos e uma parada simples por perda de comando, sem introduzir supervisores redundantes ou certificação como pré-requisito do protótipo.

## Critérios de avanço

- Estrutura: pacote reconhecido, compilável e testável.
- Aquisição: dados reais e identificados de rodas, IMU e LiDAR.
- Movimento: referências das rodas atendidas pelo controle local.
- Localização: odometria e IMU integradas com referências coerentes.
- Mapeamento: mapa obtido em ensaio real.
- Navegação: deslocamento a objetivos em ambiente conhecido.

Estrutura e fluxos de movimento/localização/mapeamento foram exercitados digitalmente em cenário sintético. Aquisição, movimento, mapeamento e navegação físicos não foram aprovados; navegação autônoma também não foi implementada na simulação.

## Recorte de simulação implementado

O software possui sensores cinemáticos virtuais, odometria, tratamento IMU, EKF e teleop por teclado nos cinco agrupadores. [Recorte local](simulacao/LEIA-ME.md) e [extensão com SLAM e grafo salvo](slam/LEIA-ME.md). Não confundir essas implementações com drivers/firmware reais.

## Arbitragem de movimento

O [árbitro manual/autônomo](arbitro/LEIA-ME.md) é um pacote separado com seleção explícita e expiração; não constitui sozinho a pilha Nav2; a composição implementada está no pacote navegacao_autonoma.

## Integração de navegação virtual

`navegacao/navegacao_autonoma` compõe Nav2 (NavFn + Regulated Pure Pursuit), costmaps e proteção de autoridade/dados. [Operação, validação e limites](navegacao/LEIA-ME.md). O árbitro continua único publicador da saída final; a integração cancela objetivos ao tomar controle manual e trava parada na perda dos dados necessários. Nenhum hardware foi acionado.
