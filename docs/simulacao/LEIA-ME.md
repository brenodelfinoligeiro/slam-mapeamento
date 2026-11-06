# Simulação cinemática com odometria, IMU e teleop

## Escopo

Simulação software em ROS 2 Jazzy, sem acesso ao robô. Não é Gazebo nem dinâmica validada: não modela contato/atrito, torque, L298N, alimentação, USB/UART reais, obstáculos ou LiDAR. Os sensores são sintéticos e a referência perfeita é publicada apenas para análise visual/testes, nunca como entrada do estimador.

A geometria usa raio e bitola de referência da descrição CAD R05, não calibração física. Resolução virtual dos encoders, escalas, ruído, bias e covariâncias são parâmetros didáticos declarados em `configuracao/simulacao.yaml`; não são medições do hardware. Contagens assinadas da simulação não comprovam sentido em encoder físico de canal único.

A extensão com [SLAM, LiDAR virtual e localização por grafo](../slam/LEIA-ME.md) é outra composição. Este guia preserva o recorte local, que por padrão não inicia mapa/laser.

## Organização implementada

- `descricao/robo_movel`: descrição existente, movida sem mudar identidade/URDF/malhas.
- `dispositivos/simulador_base`: planta cinemática, clock, encoders e IMU virtuais; dono de `msg/LeituraRodas.msg`.
- `localizacao/odometria_rodas`: integra encoders em odometria e JointState.
- `localizacao/fusao_sensores`: configura EKF do robot_localization.
- `percepcao/processamento_imu`: valida amostras e remove bias configurado do giroscópio.
- `navegacao/comando_rodas`: TwistStamped para referências de roda, com validade temporal.
- `navegacao/teleoperacao`: teclado com expiração ao soltar tecla.
- `navegacao/navegacao_simulada`: launch, parâmetros e trajetórias visuais limitadas.

Build conjunto, geração/importação ROSIDL, testes e execução DDS foram exercitados no Xeon em contêiner Jazzy. Consulte `validacao-simulacao.json` para contagens/XML e medições reais. A validação inclui execução reiniciada e captura RViz inspecionada; não é ensaio físico.

## Uso agora no Xeon com o contêiner disponível

Na raiz do workspace:

```bash
bash docs/simulacao/iniciar-conteiner.sh
```

Em outro terminal do host:

```bash
docker exec -it robo_movel_simulacao bash -c 'source /opt/ros/jazzy/setup.bash; source /work/install/setup.bash; ros2 run teleoperacao teclado --ros-args -p use_sim_time:=true'
```

O primeiro terminal mantém a simulação headless; Ctrl+C encerra. Não iniciar uma segunda instância com o mesmo nome. A imagem de teste é local e não foi publicada. Para reconstruí-la, o Dockerfile nesta pasta usa a imagem local de descrição previamente preparada. Os comandos abaixo também funcionam em uma instalação ROS com todas as dependências disponíveis.

## Uso em ambiente ROS preparado

```bash
colcon build
source install/setup.bash
ros2 launch navegacao_simulada simulacao.launch.py
```

Em outro terminal com o mesmo ambiente:

```bash
source install/setup.bash
ros2 run teleoperacao teclado --ros-args -p use_sim_time:=true
```

`w/s`: frente/ré, `a/d`: giro, `e/c`: curvas, espaço: parar, `q`: sair. Manter tecla pressionada com repetição do terminal; sem novas teclas, o comando expira. A teleop precisa de TTY real: em contêiner usar `docker exec -it` no contêiner da sessão; iniciar outro contêiner `--network none` não compartilha DDS com ele.

Para execução sem GUI: `ros2 launch navegacao_simulada simulacao.launch.py rviz:=false`.

## Fluxo e propriedade das TFs

`/cmd_vel` (TwistStamped) -> comando de rodas -> referência angular -> simulador.

Encoders -> odometria bruta (`/odometria/rodas`) e `/joint_states`; IMU -> `/imu/data_raw`. EKF usa velocidade linear das rodas, restrição lateral não holonômica e velocidade angular do giroscópio. Não recebe orientação absoluta inventada, pose perfeita ou posição de referência.

Só EKF publica `odom -> base_footprint`; RSP publica o modelo. Uma transformação estática `simulacao_mundo -> odom` representa somente a coincidência inicial de origens definida neste cenário virtual para comparação gráfica; não fornece pose perfeita ao filtro nem constitui localização global. `/simulacao/referencia` não publica TF e serve apenas à comparação. Neste launch local não há `map`/SLAM/localização global. A extensão SLAM desativa esse estático com `origem_virtual:=false` e usa outro dono para a TF global. Mesmo com a fusão local, a estimativa relativa pode derivar.

[Captura real do RViz](previa-simulacao.png). No RViz: verde = fusão, laranja = rodas, azul = referência virtual. As três trajetórias não são três medições independentes; a azul é oráculo sintético do ensaio. O modelo visual acompanha a estimativa, não a referência perfeita. Rodízio CAD sem contato corrigido artificialmente, sem massas/inércias inventadas.

## Validação reproduzível

A imagem `robo-movel/simulacao:jazzy` acrescenta `robot_localization` ao ambiente Jazzy de descrição. O host não recebe ROS nativo. `validar-conteiner.sh` monta fontes somente leitura e resultados separadamente, sem rede/dispositivos no runtime.

Executa descoberta, build, testes não vazios, teleop real por PTY, avanço/giro/ré, curva, fusão contra referência separada, expiração, comandos NaN/antigos/futuros, ownership de TF, relógio e reinício limpo. Resultados JSON/logs são produzidos por execução, nunca preenchidos manualmente com medições supostas.

Licença e contato de manutenção continuam pendentes. Malhas derivadas permanecem locais com os mesmos hashes/motivos; esta simulação não autoriza publicação ou redistribuição desses modelos.

## Problemas encontrados e corrigidos na integração

O build/unitários não detectaram um import de perfil de clock ausente na API rclpy instalada. Foi substituído por QoS explícito e ganhou smoke test ROS. Publicar no finally após shutdown do contexto também falhava; agora só se publica com contexto válido.

Referências de roda não são retransmitidas com carimbo repetido nem artificialmente renovadas: publica-se por nova entrada ou transição de parada. A velocidade em regime é verificada contra o comando, além de verificar somente que o robô se move.

A verificação de autoria TF suspende por 0,65 s **somente o processo EKF deste contêiner**, enquanto o RSP continua ativo; confirma que a aresta odom/base_footprint para e retoma com ele. Avisos de taxa do EKF na retomada desse ensaio de falha são esperados e não são apresentados como benchmark em tempo real. O helper de teste não é destinado ao robô real.

As falhas intermediárias foram preservadas fora do código, junto dos logs do ensaio, sem reescrever um teste fracassado como aprovação.

Duplicatas idênticas de comando no mesmo tick de `/clock` são idempotentes: não reemitem referência nem renovam validade. Valores diferentes reutilizando o mesmo carimbo revogam o comando. Isso foi exercitado também via `docker exec -it`, não só no teclado dentro do harness.
