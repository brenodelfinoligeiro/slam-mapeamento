# Organização dos pacotes ROS por domínio

## Decisão vigente do autor

Manter somente cinco agrupadores de pacotes específicos em `src/`: `descricao`, `localizacao`, `dispositivos`, `navegacao` e `percepcao`. Identificadores em português sem acentos; nomes de APIs externas permanecem intactos. A proposta anterior de pacotes irmãos com prefixo comum foi substituída por esta organização.

## Estado real — recorte de simulação implementado

A descrição está em `src/descricao/robo_movel/`. O recorte funcional inclui `dispositivos/simulador_base`, `localizacao/odometria_rodas`, `localizacao/fusao_sensores`, `percepcao/processamento_imu` e `navegacao/{comando_rodas,teleoperacao,navegacao_simulada}`. Possui testes e execução em contêiner Jazzy; guia e relatório correntes em `docs/simulacao/`.

A árvore e as seções restantes também descrevem componentes futuros: `comunicacao_esp` e `lidar_c1` não foram implementados, nem SLAM/Nav2. As interfaces geradas do simulador usam a instalação Python explícita, sem macro conflitante, comprovada no build e importação ROS reais.

## Árvore-alvo — não é a árvore já implementada

```text
src/
├── descricao/
│   └── robo_movel/
├── localizacao/
│   ├── odometria_rodas/
│   └── fusao_sensores/
├── dispositivos/
│   ├── comunicacao_esp/
│   └── lidar_c1/
├── navegacao/
│   └── comando_rodas/
└── percepcao/
    └── processamento_imu/
```

Os cinco agrupadores **não são pacotes ROS**: não têm `package.xml`, setup ou manifesto de metapacote. Cada pacote concreto interno tem identidade/manifesto próprios. A localização em subdiretórios não cria namespaces ROS nem nomes de importação compostos como `dispositivos/comunicacao_esp`. O colcon deve descobrir os pacotes concretos recursivamente; não colocar um manifesto no agrupador e interromper essa descoberta.

## Responsabilidades dos pacotes concretos

### descricao

`robo_movel`: URDF, malhas, RViz e launches de descrição/visualização já existentes. Movimentar arquivos sem alterar geometria, nomes de juntas, calibrações ou identidade por acidente. Não colocar processamento de sensores no pacote de descrição. A composição global futura pode ficar no pacote de navegação, sem criar um sexto agrupador.

### dispositivos

- `comunicacao_esp`: único dono da UART; codec e transporte; envio de referências de roda e recebimento de contagens/amostras inerciais, tempos e diagnósticos. Reconexão descarta comandos vencidos. Não faz fusão nem PID ROS.
- `lidar_c1`: integração/parametrização de driver existente compatível com o C1. Publica LaserScan em `scan`; o driver externo mantém seu nome/API. Não inventar interface física ou porta nem criar adaptador de retransmissão se launch/configuração bastar.
As interfaces específicas pertencem ao pacote que fornece o recurso. Não há pacote central de interfaces; a decisão de propriedade está na seção abaixo.

### percepcao

`processamento_imu`: converte as amostras recebidas da ponte para SI, trata bias, eixos, timestamps e covariâncias e publica `sensor_msgs/msg/Imu`. A aquisição I²C fica no ESP; não criar um segundo driver I²C na Pi nem orientação absoluta fictícia para a MPU-6050.

Processamento futuro de varreduras/obstáculos pertence a este domínio; não implementado nem necessário para organizar a árvore inicial.

### localizacao

- `odometria_rodas`: contagens/estado das rodas para odometria bruta e `JointState`. Distinguir sentido medido de sentido inferido; tratar reset, wrap e relógios inválidos.
- `fusao_sensores`: configuração/launch de estimador como `robot_localization`, combinando odometria e IMU validadas, sem reescrever EKF nem tratar dados correlacionados como independentes sem justificativa.

SLAM/mapeamento futuro fica aqui como pacote específico, **não como sexto agrupador `mapeamento`**. Não é parte da primeira implementação.

### navegacao

`comando_rodas`: recebe velocidade linear/angular, aplica cinemática diferencial e limites/expiração e envia referência das rodas à ponte. O domínio absorve o antigo agrupador de controle, sem pasta-raiz `controle`. Raio e distância entre rodas precisam de uma fonte de parâmetros consistente com a odometria, sem medidas físicas inventadas.

Planejamento/seguimento de trajetórias e integração Nav2 futuros entram neste domínio, em pacotes concretos quando necessários; não foram implementados por esta decisão.

## Interfaces pertencem a cada pacote

Decisão do autor: não criar pacote central de interfaces. Cada pacote mantém seus próprios contratos específicos em `msg/`, `srv/` e/ou `action/`, somente quando necessários. Alterar um componente não deve exigir editar um pacote global de mensagens.

Exemplo previsto, não implementado:

```text
dispositivos/comunicacao_esp/
├── package.xml
├── CMakeLists.txt
├── msg/
│   ├── ComandoRodas.msg
│   ├── LeituraRodas.msg
│   └── AmostraInercial.msg
└── [implementação da ponte]
```

- A ponte é dona dos contratos do enlace ESP. Consumidores usam `comunicacao_esp/msg/LeituraRodas`, por exemplo, e declaram dependência no pacote proprietário. O agrupador `dispositivos` não faz parte do nome do tipo.
- `comando_rodas` consome velocidade ROS padronizada e produz o comando esperado pela ponte, sem definir uma cópia concorrente desse contrato.
- `odometria_rodas` consome a leitura da ponte e publica `nav_msgs/msg/Odometry` e `sensor_msgs/msg/JointState`.
- `processamento_imu` recebe a amostra da ponte e publica `sensor_msgs/msg/Imu`; futuros serviços específicos de processamento pertencem a esse pacote, caso necessários.
- `lidar_c1` usa `sensor_msgs/msg/LaserScan`; `fusao_sensores` usa entradas/saídas padronizadas quando suficientes. Não criar tipos próprios só para preencher uma pasta de interfaces.
- A mesma informação compartilhada tem um único tipo proprietário: não duplicar `.msg` em produtor e consumidor, pois layouts iguais em pacotes diferentes não significam a mesma identidade ROS.
- Dependências continuam existindo: mudar um contrato pode exigir recompilar/ajustar seus consumidores. Não prometer independência total ou eliminação do acoplamento de API.
- Evitar ciclos: contratos da ponte não importam interfaces dos processadores que já dependem da ponte; parâmetros/configuração não justificam dependência de retorno.

### Restrição de build confirmada na documentação ROS 2 Jazzy

Pacotes que geram interfaces próprias usam `ament_cmake` e ROSIDL; `ament_python` puro não gera esses tipos. Pacotes sem geração de interfaces podem continuar `ament_python`.

A documentação oficial alerta que chamar `rosidl_generate_interfaces` e `ament_python_install_package` no mesmo projeto CMake não funciona e recomenda separar a geração. Aqui, a preferência do autor é manter a propriedade local e não adotar um pacote global. Logo, **não usar essa combinação incompatível nem trocar a linguagem dos nós silenciosamente**. Se houver nós Python no mesmo pacote gerador, o empacotamento deverá usar instalação explícita de executáveis/implementação sem a macro conflitante e ser provado em um build isolado, com geração, importação instalada e execução reais. Essa alternativa ainda não foi exercitada neste projeto; não tratá-la como implementação pronta.

Fontes: `fontes-interfaces-locais.json`, com URLs oficiais, hashes e trechos. Não foram criados arquivos `.msg`, `.srv` ou `.action` nesta atualização do plano.

## Fluxos previstos

```text
cmd_vel -> navegacao/comando_rodas -> dispositivos/comunicacao_esp -> UART -> ESP
ESP -> dispositivos/comunicacao_esp -> localizacao/odometria_rodas
ESP -> dispositivos/comunicacao_esp -> percepcao/processamento_imu
odometria + IMU -> localizacao/fusao_sensores -> odom
C1 -> dispositivos/lidar_c1 -> scan
```

Os caminhos acima expressam agrupador/pacote no projeto, não sintaxe de tópicos ROS. Os contratos concretos dos tópicos, protocolo UART, baudrate, GPIOs e frequências ainda precisam de definição. Controle PI/PID das rodas e aquisição de encoders/MPU permanecem no ESP. Firmware em `programa_esp/`, fora dos pacotes ROS; plataforma ainda pendente.

## TF e limites preservados

- RSP publica relações do modelo; rodas usam `joint_states` reais no launch de runtime e estados de demonstração apenas na visualização.
- Estimador local publica sozinho `odom -> base_footprint`. Sem fusão, um modo explícito pode selecionar odometria das rodas; nunca dois donos da mesma TF.
- SLAM/localizador futuro publica `map -> odom`, com um único dono por modo.
- Frames de suporte do CAD não são extrínsecas calibradas nem plano óptico do C1. Sem massas, calibração, torque ou orientação absoluta inventados.
- A arquitetura vigente usa Pi 5, ESP, UART, L298N, encoders MH-Sensor-Series, MPU-6050 e C1. Não retomar ponte MOSFET ou USB como decisão atual.

## Sequência de implementação futura

1. Testar em RED a descoberta dos pacotes concretos dentro dos agrupadores e os caminhos revisados da descrição. Fazer snapshot de fonte/build/install/log antes de migrar.
2. Mover a descrição para seu agrupador, atualizar raízes/caminhos em testes/geradores/docs e verificar instalação nova, URDF, hashes, TF e RViz. Não mudar geometria ou nomenclatura de juntas nesta operação.
3. Fechar contratos no próprio pacote proprietário, provar o build ROSIDL/instalação escolhido sem macros Python conflitantes e implementar ponte UART com testes de fragmentação/corrupção/validade/reinício e porta pseudo-terminal, sem hardware.
4. Implementar comandos e odometria com testes de cinemática/sinais/limites/expiração/contagens; separar fonte do sentido de simples hipótese de comando.
5. Implementar processamento inercial e integração do C1; só então configurar a fusão com testes de tempo, covariâncias e propriedade das TFs.
6. Exercitar `colcon list/build/test` apontando a `src/` inteira, conferir os casos reais no XML, importação instalada fora da fonte e recorte extraído em workspace novo. Contêiner Jazzy isolado é ambiente de teste anterior, não seleção da distribuição da Pi.

## Preservação

Workspace canônico `/home/lamggm/projects/robo_movel_ws`; apelido fora das identidades ROS. Preservar mudanças locais, arquivos CAD/STL, origens/hash/licenças, histórico, README do proprietário e o arquivo protegido `AGENTS.md`. Sem commit/push, deploy ou acesso ao hardware nesta atualização. Resultados da renomeação anterior continuam em `docs/descricao-ros/validacao-nomenclatura.json` e não comprovam migração para esta árvore-alvo.
