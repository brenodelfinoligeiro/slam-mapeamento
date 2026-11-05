# 1. Visão geral

## Finalidade

O Slamderson é um trabalho acadêmico de robótica móvel baseado em um carrinho de tração diferencial. O projeto pretende integrar acionamento das rodas, odometria, medição inercial e LiDAR para estudar localização, construção de mapas e navegação.

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

O pacote `src/slamderson` contém metadados `ament_python`, módulos vazios em português, pastas de recursos reservadas e testes estruturais. Não há executáveis registrados. Os diretórios de mapas e configurações ainda não contêm resultados ou parâmetros de hardware.

As ferramentas colcon foram usadas em ambiente isolado. Não foi instalado nem selecionado um ROS 2 completo nesta tarefa. Não confundir importação de módulos Python com execução de nós ou comunicação DDS.

## Escopo proporcional

Trata-se de um protótipo didático pequeno, não de um robô industrial. Manter cuidados elétricos básicos e uma parada simples por perda de comando, sem introduzir supervisores redundantes ou certificação como pré-requisito do protótipo.

## Critérios de avanço

- Estrutura: pacote reconhecido, compilável e testável.
- Aquisição: dados reais e identificados de rodas, IMU e LiDAR.
- Movimento: referências das rodas atendidas pelo controle local.
- Localização: odometria e IMU integradas com referências coerentes.
- Mapeamento: mapa obtido em ensaio real.
- Navegação: deslocamento a objetivos em ambiente conhecido.

Somente a primeira categoria foi exercitada pelo assistente até esta etapa.
