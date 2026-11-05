# 4. Comunicação UART

## Objetivo

Utilizar um único enlace bidirecional entre Raspberry e ESP para comandos e telemetria. Os dois sentidos têm funções distintas:

- Raspberry -> ESP: referências de movimento e comandos necessários à operação.
- ESP -> Raspberry: contagens/velocidades das rodas, aceleração e velocidade angular da MPU-6050, marcas temporais e estado pertinente.

A IMU continua sendo lida pelo ESP. Não é necessário um cabo serial separado por sensor e não se pretende transportar o barramento I²C diretamente até a Raspberry.

## Estado do contrato

O protocolo ainda não foi implementado. Não existem valores finais de taxa de transmissão, frequência de publicação, tamanho de mensagem, tipos binários, ordem de bytes, polinômio de CRC ou estrutura de cabeçalho.

Os tópicos ROS também são propostas. Identificadores convencionais como `cmd_vel`, `odom`, `imu/data_raw` e `scan` poderão ser usados conforme os pacotes adotados, sem tradução que quebre interfaces externas.

## Requisitos a fechar na implementação

- Delimitar mensagens e permitir recuperação após bytes perdidos ou dados de inicialização.
- Identificar tipo, versão, tamanho e sequência quando necessários.
- Definir verificação de integridade e limites de valores.
- Especificar unidades e convenções de sentido/eixos.
- Distinguir instante de aquisição no ESP do instante de recepção na Raspberry.
- Definir tratamento de reinício dos contadores e do relógio do ESP.
- Não reaplicar mensagens antigas após reconexão ou atraso acumulado.
- Parar o acionamento ao perder comandos válidos pelo intervalo escolhido para o protótipo.

Esses itens são critérios de projeto, não campos ou códigos já disponíveis. Não preencher a documentação com mensagens de exemplo apresentadas como capturas reais.

## Conteúdo esperado da telemetria

Documentar a origem de cada campo antes de programar:

- contagem bruta por roda e convenção de bordas;
- velocidade estimada por roda e unidade;
- distinção entre módulo medido e sinal inferido pelo comando;
- aceleração e velocidade angular com ordem dos eixos;
- marca temporal e unidade de tempo;
- indicadores simples de validade, se necessários.

No ROS, aceleração é normalmente representada em m/s² e velocidade angular em rad/s nas mensagens padronizadas. A conversão a partir dos registros da IMU depende das faixas configuradas, ainda não escolhidas. Não publicar uma orientação fictícia quando só houver dados inerciais brutos.

## Implementação e testes previstos

Concentrar abertura de porta, enquadramento e reconexão em `dispositivos/esp32_uart`. Separar a interpretação das mensagens do acesso ao sistema operacional para permitir testes com bytes de entrada, sem hardware.

Testar mensagem completa, fragmentação, corrupção, sequência antiga, reinício e ausência de dados. Quando o hardware existir, registrar capturas reais identificadas com versão do programa, configuração da porta e condições do ensaio. Nenhum desses testes de comunicação foi realizado nesta etapa.
