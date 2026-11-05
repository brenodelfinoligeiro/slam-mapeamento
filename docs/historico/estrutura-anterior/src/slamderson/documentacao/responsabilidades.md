# Responsabilidades das pastas

Este documento descreve a organização proposta do trabalho acadêmico, não uma lista de nós já implementados. As bibliotecas citadas são candidatas de integração; a distribuição ROS 2 e suas interfaces ainda serão verificadas.

## Código — `slamderson/`

### `dispositivos/`

Interface com o hardware: comunicação, aquisição, marcas temporais e representação dos dados recebidos.

- `esp32_uart/`: único responsável pela porta UART entre Raspberry e ESP. Serializa comandos e decodifica dados dos codificadores de rotação e da IMU. Reconexão e delimitação das mensagens pertencem a esta interface. Não abrir a mesma porta em dois módulos independentes.
- `mpu6050/`: pasta opcional para conversão de unidades e eixos e representação dos dados da IMU recebidos pelo ESP. Não representa outra ligação I²C na Raspberry ou outra porta serial. Inicialmente o tratamento pode permanecer em `esp32_uart/`.
- `lidar_c1/`: adaptação e configuração do controlador de dispositivo que publicará `sensor_msgs/LaserScan`. Preferir uma implementação existente do fabricante; não reimplementar o protocolo sem necessidade. Ligação e parâmetros ainda estão pendentes.

### `controle/`

Tratamento dos comandos, limites e cinemática diferencial no lado ROS 2. Quando necessário, transforma velocidade linear e angular em referências para as rodas. Se `diff_drive_controller` for adotado, reutilizar sua cinemática em vez de criar outra conversão concorrente.

O cálculo inicial da odometria das rodas a partir das contagens também pode ficar nesta camada, separado do transporte serial. O PI/PID da velocidade das rodas continua no programa embarcado do ESP. Não duplicar o controlador de trajetória do Nav2 sem necessidade demonstrada.

### `localizacao/`

Estima posição, orientação e movimento do robô. Na primeira etapa, combinar odometria das rodas e IMU para obter odometria local filtrada, por exemplo com `robot_localization`. Ao navegar em mapa conhecido, configurar localização global, por exemplo com AMCL.

A fusão não transforma um codificador de canal único em medição direta do sentido e não transforma a MPU-6050 em bússola.

### `mapeamento/`

Construção de mapas com o LiDAR e a estimativa de movimento. Integrar uma solução como `slam_toolbox`, configurar o modo de operação e salvar ou carregar mapas. Não implementar SLAM próprio apenas para preencher a pasta.

Durante o mapeamento, o sistema de SLAM normalmente fornece a transformação `map -> odom`. Em mapa conhecido, um localizador como AMCL pode assumir essa responsabilidade. Os modos precisam ser explícitos, sem dois publicadores concorrentes da mesma transformação.

### `navegacao/`

Integração de navegação, preferencialmente com Nav2: objetivos, planejamento, acompanhamento de trajetórias, mapas de custo e comportamentos. Os parâmetros ficam em `configuracao/`; a composição dos processos fica em `inicializacao/`. Acrescentar código próprio somente quando a integração exigir.

### `percepcao/`

Processamento adicional de sensores: filtros de varreduras, agrupamento e detecção de objetos ou extração de informações. Não confundir com a interface de aquisição do LiDAR, que pertence a `dispositivos/`.

A pasta pode permanecer reservada no início: dados adequados do LiDAR, SLAM e mapas de custo podem atender ao primeiro protótipo. Não criar processamento sem uma necessidade observada.

## Recursos do pacote

- `inicializacao/`: arquivos de composição e inicialização. Poderão existir modos de dispositivos, mapeamento e navegação; nenhum deles foi implementado.
- `configuracao/`: arquivos YAML de comunicação, LiDAR, filtros, fusão, SLAM e Nav2, conforme as integrações escolhidas.
- `descricao/`: URDF/Xacro, dimensões, articulações e posicionamento dos sensores. Utilizar medidas reais; `robot_state_publisher` poderá publicar as transformações fixas.
- `mapas/`: mapas adquiridos e seus metadados. Não apresentar dados sintéticos como medições reais.
- `visualizacao/`: configurações do RViz para robô, TF, odometria, varreduras do LiDAR, mapas e trajetórias.
- `documentacao/`: arquitetura, ligações, protocolo UART, uso e calibração.
- `recursos/`: marcador de registro do pacote no índice ament; não contém um controlador de dispositivo.
- `testes/`: testes de interpretação de mensagens, unidades, eixos, cinemática e integração conforme o código evoluir. Os testes atuais verificam apenas a estrutura e sua localização em português.

## Fluxo de dados e transformações — proposta

1. Codificadores de rotação e MPU-6050 são lidos pelo ESP; os dados seguem por UART para `dispositivos/`.
2. As contagens dão origem à odometria não filtrada; os dados inerciais são representados em mensagem própria. O contrato definitivo de tópicos, unidades e marcas temporais ainda será definido.
3. `localizacao/` funde odometria e IMU. Nesse arranjo, apenas o estimador local publica `odom -> base_link`.
4. A interface do C1 publica a varredura com referência coerente; `descricao/` representa a posição real do sensor.
5. SLAM constrói o mapa e fornece `map -> odom`; em modo de mapa conhecido, AMCL poderá assumir essa transformação.
6. `navegacao/` gera comandos; `controle/` adapta as referências quando necessário; `dispositivos/` transmite ao ESP, que fecha o PI.

Os nomes convencionais `map`, `odom`, `base_link` e `base_footprint` permanecem identificadores ROS. Os parâmetros e prefixos definitivos serão escolhidos na integração. A separação de pastas não exige um nó ROS por pasta.

## Ordem recomendada

Comunicação UART e dados reais → varreduras do C1 e transformações TF → odometria local → mapeamento → navegação. `percepcao/` e código adicional de `controle/` evoluem somente quando necessários. A primeira entrega é um protótipo didático funcional, não uma arquitetura industrial.
