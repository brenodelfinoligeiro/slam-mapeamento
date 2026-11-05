---
tipo: decisao
estado: confirmado_pelo_autor
atualizado: 2026-11-04
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

Estas são decisões do projeto, não afirmações retiradas de um catálogo. Não consultar documentos históricos como se sobrepusessem decisões posteriores do autor.

## Limites preservados

O autor considera, ainda sem decisão fechada, usar pilhas AA para os motores e um powerbank separado para a Raspberry Pi 5. Quantidade e química das AA, porta-pilhas, modelo e capacidade do powerbank, alimentação do ESP, retenção mecânica e autonomia permanecem pendentes. Verificar a capacidade elétrica do powerbank, não somente mAh.[23]

O autor informa que os motores são de 12 V; essa especificação ainda precisa ser conferida na etiqueta/datasheet do modelo exato. Oito alcalinas AA em série correspondem a 12 V nominais, mas não comprovam que o conjunto sustente a corrente de partida nem compensam a queda da L298N.

Placa ESP final, bateria dos motores, GPIOs, taxa/protocolo UART, revisão exata dos módulos dos sensores, geometria, correntes dos motores e distribuição ROS 2 permanecem pendentes.

O programa atual é um esqueleto de pacote `ament_python`, sem nós de hardware implementados. Testar a estrutura Python não valida ROS 2 completo, movimento, UART, IMU ou SLAM.

## Ligações conceituais

Referência de velocidade -> ESP -> direção/PWM -> L298N -> motores.
Codificadores e IMU -> ESP -> UART -> Raspberry -> odometria/localização.
LiDAR -> interface ainda a confirmar -> Raspberry -> mapeamento/navegação.

[[01-componentes/Encoder-MH-Sensor-Series]] · [[01-componentes/L298N]] · [[01-componentes/MPU-6050]] · [[06-ideias/Ideias-e-pendencias]]

## Sources

[23] https://pip.raspberrypi.com/documents/RP-009856-WP — Raspberry Pi Ltd — USB Power Delivery on Raspberry Pi 5
