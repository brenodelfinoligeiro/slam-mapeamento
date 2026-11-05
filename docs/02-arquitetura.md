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
5. Uma integração como `robot_localization` poderá fundir as medições para produzir odometria local.
6. As varreduras do C1 e a odometria poderão alimentar uma solução como `slam_toolbox`.

Os pacotes citados são candidatos, não dependências de execução já integradas.

## Transformações de referência

A cadeia convencional proposta é `map -> odom -> base_link`, com referências adicionais para os sensores. Os identificadores padronizados permanecem inalterados para compatibilidade.

- O estimador local, quando adotado, será o único publicador de `odom -> base_link`.
- O SLAM fornecerá `map -> odom` no modo de construção do mapa.
- Em modo de mapa conhecido, um localizador como AMCL poderá assumir `map -> odom` em vez do SLAM.
- As posições fixas dos sensores deverão vir da descrição geométrica medida do robô.

Não permitir dois publicadores concorrentes da mesma transformação. Valores geométricos, prefixos e eventual uso de `base_footprint` ainda serão definidos.

## Limitações observáveis

Um codificador de canal único mede o módulo do movimento. O sentido comandado fornece uma hipótese, que pode ser confrontada com o giro medido pela IMU. Isso não garante distinguir avanço de ré em translação reta a velocidade constante. Reversão com embalo, deslocamento externo e patinagem podem invalidar o sinal presumido.

Não resolver falta de informação atribuindo certeza artificial a um filtro. Dados brutos, sentido inferido e indicadores de confiança devem permanecer distinguíveis.
