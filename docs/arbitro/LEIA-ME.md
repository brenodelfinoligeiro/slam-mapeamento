# Árbitro de movimentação manual e autônoma

## Responsabilidade

`src/navegacao/arbitro` seleciona exclusivamente uma origem de velocidade. Não planeja caminhos, não localiza, não controla PI/PID das rodas e não depende de Nav2. Fica em `navegacao`, sem novo agrupador ou pacote central de interfaces.

```text
teleop -> /cmd_vel_manual ---------+
                                  +-> arbitro -> /cmd_vel -> comando_rodas -> base/ESP
Nav2 + proteção -> /cmd_vel_autonomo --+
```

Nas três interfaces de velocidade o tipo é **geometry_msgs/TwistStamped**, com comando planar no corpo do robô. Frame aceito: `base_footprint` ou vazio (normalizado para o corpo). O carimbo original inteiro é preservado; o árbitro não rejuvenesce comandos. A composição Nav2 atual habilita esse tipo nos produtores Jazzy e passa pela proteção de autonomia; veja [integração](../navegacao/LEIA-ME.md).

## Seleção e parada

- Inicia **manual**, sem comando e com saída zero.
- `/arbitro/automatico` — `std_srvs/SetBool`: true seleciona autônomo, false seleciona manual.
- `/arbitro/parar` — `std_srvs/Trigger`: trava estado parado. Comandos não rearmam; selecionar um modo explicitamente para retomar.
- `/arbitro/estado` — `std_msgs/String` com JSON de `modo`, `ativo`, `motivo`, `geracao`; reliable/transient-local para observador novo.

Cada seleção explícita abre uma época, descarta o comando anterior e zera a saída. Exige carimbo posterior à barreira ROS da seleção + tolerância futura (padrão 0,05 s), evitando aceitar comandos enfileirados antes da troca. A origem não selecionada é ignorada e **não existe fallback automático**, nem prioridade pela última mensagem recebida.

O prazo padrão de comando é **0,3 s**, verificado tanto em tempo ROS quanto monotônico de recepção. Duplicata idêntica é idempotente, sem renovar validade; mesmo carimbo com valores diferentes revoga a entrada. Carimbos antigos/futuros fora da tolerância, NaN/Inf e componentes não planares são rejeitados. Retrocesso dos relógios trava parado e exige seleção explícita. Os parâmetros `prazo_comando` e `tolerancia_futuro` são somente leitura após inicialização.

O timer usa STEADY_TIME: pausar `/clock` não congela o watchdog. Limites/cinemática de rodas continuam no consumidor `comando_rodas`; o árbitro não inventa limites físicos.

## Uso em ROS preparado

Depois de build/source do workspace:

```bash
ros2 launch arbitro simulacao_arbitrada.launch.py
```

Em outro terminal do mesmo ambiente/DDS:

```bash
ros2 run teleoperacao teclado --ros-args -p use_sim_time:=true -r /cmd_vel:=/cmd_vel_manual
```

Selecionar autônomo, voltar ao manual ou travar parada:

```bash
ros2 service call /arbitro/automatico std_srvs/srv/SetBool '{data: true}'
ros2 service call /arbitro/automatico std_srvs/srv/SetBool '{data: false}'
ros2 service call /arbitro/parar std_srvs/srv/Trigger '{}'
ros2 topic echo /arbitro/estado
```

Sem publicador autônomo, selecionar autônomo mantém saída zero. O teclado exige TTY real; `emulate_tty` em stdout de launch não cria entrada interativa. Em contêiner usar docker exec -it **no mesmo contêiner** e o mesmo remapeamento. Não iniciar outro contêiner --network none esperando compartilhar DDS.

Para iniciar somente o árbitro, sem planta:

```bash
ros2 launch arbitro arbitro.launch.py
# Em simulação externa:
ros2 launch arbitro arbitro.launch.py use_sim_time:=true
```

A composição nova incorpora base + árbitro. **Os launches legados não foram alterados**: iniciar o fluxo antigo de SLAM/teleop não insere o árbitro implicitamente. Na integração Nav2, o publicador autônomo e a teleop devem usar as entradas, e somente o árbitro deve publicar a saída final.

## Limites importantes

- É seleção de comandos, não controle de ações NavigateToPose. Trocar modo não cancela objetivos upstream. Na futura integração, o coordenador de navegação deverá cancelar/pausar o objetivo quando necessário; voltar explicitamente ao autônomo pode admitir comandos novos de um objetivo ainda ativo.
- Não é E-stop certificado nem substitui watchdog/parada elétrica do ESP. Se o árbitro morrer, o timeout do consumidor continua sendo necessário.
- Não autentica publicadores ROS: outro nó pode escrever diretamente em /cmd_vel. A unicidade é contrato da composição e foi conferida no grafo isolado, não barreira de segurança cibernética.
- Não inspeciona SLAM, obstáculos ou sensores; gates específicos do modo autônomo pertencem à integração seguinte.
- Ensaios usam velocidades autônomas sintéticas para provar a arbitragem, não demonstram Nav2/navegação/hardware.

## Verificação

`validar-conteiner.sh` usa a imagem Jazzy local já preparada, fonte somente leitura, sem rede/dispositivos, e resultados em diretório novo:

```bash
bash docs/arbitro/validar-conteiner.sh /caminho/absoluto/novo
```

Exercita build/testes, duas fontes concorrentes, troca neutra, parada travada, expiração, replay, NaN, carimbo inteiro, clock pausado, rodas/planta, teclado real remapeado e reinício completo em manual. Contagens e recibos reais são consolidados em `validacao-arbitro.json` quando o ensaio termina; não somar wrapper CTest ou repetir contagem da mesma suíte.

## Integração Nav2 atual

O árbitro isolado continua sem controlar ações. Na [composição de navegação](../navegacao/LEIA-ME.md), `protecao_autonomia` monitora autoridade/dados, cancela objetivos e bloqueia retomada de objetivo antigo. Os ensaios sintéticos deste recorte não são a evidência de navegação; o relatório da integração é separado.
