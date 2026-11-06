# 2. Arquitetura e fluxos de dados

## Distribuição de responsabilidades

```text
Raspberry Pi 5 / ROS 2
    | comandos de velocidade
    | UART bidirecional
    | contagens, velocidades e dados da IMU
ESP
    +-- entradas dos codificadores de rotação
    +-- I²C local -> MPU-6050
    +-- controle PI das rodas -> direção/PWM -> L298N -> motores

LiDAR C1 -> interface a confirmar -> aquisição de varreduras no ROS 2
```

O desenho indica responsabilidades, não pinos, taxas ou pacotes de mensagens já implementados.

## Computador embarcado

A Raspberry executará comunicação com o ESP, representação dos dados em mensagens ROS, estimativa de estado, integração do LiDAR, mapeamento e navegação. A pilha de navegação poderá gerar velocidade linear e angular; uma única camada deverá convertê-las em referências das rodas quando essa conversão ficar na Raspberry.

## Microcontrolador

O ESP adquire codificadores e IMU e fecha o controle PI de velocidade. Esse laço não depende da latência de ida e volta pela UART. Saturação, tratamento de reversão e parada por ausência de comando pertencem à implementação local proporcional ao protótipo.

O acionamento atual será feito por módulo L298N: entradas de direção por canal e PWM nas entradas de habilitação. A L298N não lê os codificadores nem fecha o controle de velocidade; isso permanece no ESP. A ligação funcional está no [capítulo de componentes](03-componentes-e-ligacoes.md).

O software ROS não deverá abrir uma segunda porta serial para cada sensor. `dispositivos/esp32_uart` será o responsável pelo enlace; `dispositivos/mpu6050` é apenas uma possível separação do tratamento das amostras recebidas, não outro acesso I²C na Raspberry.

## Fluxo de estimativa

1. Codificadores produzem contagens e estimativas de velocidade das rodas.
2. A MPU-6050 fornece aceleração e velocidade angular.
3. O ESP transmite dados e marcas temporais.
4. O lado ROS representa a odometria de rodas e a IMU separadamente.
5. Na simulação, `robot_localization` já funde velocidades das rodas e giroscópio para produzir odometria local.
6. LiDAR virtual gera `/scan`; SLAM Toolbox usa os raios e TF de odometria para construir mapa/estimar pose.

Essas integrações já executam no recorte virtual; não constituem integração do C1 físico ou da UART. [Operação e limites](slam/LEIA-ME.md).

## Transformações de referência

A cadeia implementada na composição SLAM é `map -> odom -> base_footprint -> base_link`, com referências adicionais para sensores.

- EKF é o único publicador de `odom -> base_footprint`.
- SLAM Toolbox publica `map -> odom`, nos modos mapeamento e localização por grafo.
- RSP publica a geometria e os estados de juntas.
- O sensor virtual define `laser_simulado` a partir de `lidar_mount_link`; não é calibração do C1 real.
- AMCL continua não implementado; se adotado posteriormente, substitui o dono global, sem competir com o SLAM.

O alinhamento estático anterior `simulacao_mundo -> odom` é desativado ao compor SLAM. A identidade virtual `simulacao_mundo -> map` serve à comparação, não determina a pose. A referência perfeita só gera sensores e serve a testes/visualização, nunca é medição de posição para os estimadores.

## Limitações observáveis

Um codificador de canal único mede o módulo do movimento. O sentido comandado fornece uma hipótese, que pode ser confrontada com o giro medido pela IMU. Isso não garante distinguir avanço de ré em translação reta a velocidade constante. Reversão com embalo, deslocamento externo e patinagem podem invalidar o sinal presumido.

Não resolver falta de informação atribuindo certeza artificial a um filtro. Dados brutos, sentido inferido e indicadores de confiança devem permanecer distinguíveis.

## Integração de navegação virtual

`navegacao/navegacao_autonoma` compõe Nav2 (NavFn + Regulated Pure Pursuit), costmaps e proteção de autoridade/dados. [Operação, validação e limites](navegacao/LEIA-ME.md). O árbitro continua único publicador da saída final; a integração cancela objetivos ao tomar controle manual e trava parada na perda dos dados necessários. Nenhum hardware foi acionado.
