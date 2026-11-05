# Responsabilidades das pastas

## Separação principal

- `docs/`: documentação acadêmica, arquitetura, procedimentos e registros.
- `src/slamderson/`: código, testes, metadados e recursos de execução do pacote.

As pastas separam responsabilidades. Não obrigam um processo ROS por diretório e não comprovam funcionalidade implementada.

## Módulos em `src/slamderson/slamderson/`

### `dispositivos/`

Interfaces com os equipamentos físicos, representação das aquisições e transporte dos dados.

- `esp32_uart/`: único responsável pela UART entre Raspberry e ESP. Envia referências e recebe dados dos codificadores e da IMU. Delimitação de mensagens e reconexão ficam nesta interface, sem abertura duplicada da mesma porta.
- `mpu6050/`: separação opcional para conversão e representação das amostras inerciais recebidas. Não corresponde a outro acesso I²C na Raspberry. Inicialmente esse tratamento pode ficar na interface UART.
- `lidar_c1/`: integração de um controlador de dispositivo existente para o C1. Ligação e parâmetros ainda serão confirmados; não reimplementar o protocolo sem necessidade.

### `controle/`

Tratamento de comandos e cinemática diferencial no lado ROS 2. Quando necessário, converte velocidade linear/angular em referências das rodas e calcula odometria de rodas a partir das contagens.

Se uma integração com `diff_drive_controller` for adotada, reutilizar essa cinemática em vez de criar outro caminho concorrente. O PI/PID das rodas permanece no ESP. Não duplicar o controlador de trajetória do Nav2 sem necessidade.

### `localizacao/`

Estimativa de posição, orientação e movimento. Fusão de odometria das rodas e IMU, possivelmente com `robot_localization`; localização global em mapa conhecido, por exemplo com AMCL, em modo explicitamente escolhido.

A fusão não elimina a ambiguidade de sentido de codificadores de canal único e não cria rumo absoluto na MPU-6050.

### `mapeamento/`

Construção de mapas usando LiDAR e estimativa de movimento, com possível integração de `slam_toolbox`. Responsável pela operação de mapeamento e gestão dos mapas resultantes, não pela implementação obrigatória de SLAM próprio.

### `navegacao/`

Integração de objetivos, planejamento, acompanhamento de trajetória e mapas de custo, preferencialmente reutilizando Nav2. Configurações vão para `configuracao/`; composição dos processos vai para `inicializacao/`.

### `percepcao/`

Processamento adicional de dados: filtros de varredura, agrupamentos, detecção de objetos ou extração de informações. O controlador do LiDAR continua em dispositivos. Pode permanecer vazia enquanto os dados existentes atenderem às necessidades.

## Recursos em `src/slamderson/`

- `inicializacao/`: arquivos para compor e iniciar as partes implementadas. Ainda reservada.
- `configuracao/`: parâmetros YAML reais das integrações. Não contém valores presumidos.
- `descricao/`: URDF/Xacro e malhas com geometria medida do robô.
- `mapas/`: mapas gerados ou selecionados para execução; relatórios dos ensaios ficam em `docs/`.
- `visualizacao/`: configurações do RViz, não relatórios ou imagens de resultados.
- `recursos/`: marcador do pacote para o índice ament.
- `testes/`: verificações automatizadas da estrutura e, futuramente, do código. Explicações metodológicas extensas ficam em `docs/`.

Pastas ainda sem recursos reais usam marcadores vazios `.gitkeep`; não precisam de um manual em cada diretório.

## Fluxo de operação proposto

Codificadores e MPU-6050 -> ESP -> UART -> dispositivos -> odometria/IMU -> localização.
LiDAR C1 -> dispositivos -> varredura -> mapeamento e navegação.
Navegação -> comandos -> controle, quando necessário -> UART -> ESP -> PI das rodas -> direção/PWM -> L298N -> motores.

A responsabilidade por cada transformação TF deve ser única. Consulte [arquitetura](02-arquitetura.md) para a cadeia proposta e [comunicação](04-comunicacao-uart.md) para os limites do contrato ainda não implementado.
