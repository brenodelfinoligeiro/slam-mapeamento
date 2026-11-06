# Navegação autônoma Nav2 arbitrada

## Estado desta integração

**Navegação real Nav2 aprovada no recorte virtual AMD64/Jazzy.** Três objetivos NavigateToPose, desvio geométrico e retorno passaram, assim como cancelamento, tomada manual, perdas de dados e cliente CLI. Recarga em localização, RViz real e o helper público por PTY também passaram; o [relatório executado](validacao-navegacao.json) identifica as execuções e seus limites. Não é aprovação de hardware.

## Imagens

[Galeria pública: trajeto e métricas do ensaio](imagens/LEIA-ME.md), com PNGs, SVGs editáveis e dados de entrada. A captura RViz com CAD permanece local por licença pendente.

## Fluxo

```text
/scan + TF odométrico -> SLAM Toolbox -> /map + map -> odom
/odom + mapa + scan + TF -> NavFn / Regulated Pure Pursuit / BT Navigator
                            |
                       /cmd_vel_nav2 (TwistStamped)
                            |
                    protecao_autonomia
                            |
                     /cmd_vel_autonomo ----+
/cmd_vel_manual --------------------------+-> arbitro -> /cmd_vel -> comando_rodas
```

Os dois launchs antigos de SLAM e da simulação ficam intactos. Use a composição explícita de `navegacao_autonoma`. Ground truth somente gera medições virtuais no LiDAR e avalia resultados no ensaio; não é entrada de SLAM, Nav2 ou proteção.

## Escopo da configuração

NavFn e Regulated Pure Pursuit diferencial, costmap global em `map` e local rolante em `odom`, com obstáculos de `/scan`. Raio conservador de planejamento 0,18 m, derivado das malhas R05 e margem proposta; veja `geometria-planejamento.json`. Não é medição/calibração física. A margem já está no raio, sem padding implícito adicional. Espaço desconhecido não é declarado livre para simplificar o teste.

Comandos e PI/PID de cada roda continuam em suas camadas; Nav2 fornece velocidade corporal e não PWM. Velocidade linear desejada de 0,16 m/s, rotação de alinhamento de 0,5 rad/s e aceleração angular de 1,2 rad/s² são parâmetros virtuais. Não se declara rampa linear física nem calibração de motores.

## Iniciar no ambiente Jazzy preparado

```bash
bash docs/navegacao/iniciar-conteiner.sh
```

Ou depois de build/source num ambiente ROS com as dependências instaladas:

```bash
ros2 launch navegacao_autonoma navegacao_simulada.launch.py rviz:=true
```

O helper de contêiner é headless, sem rede externa/dispositivos e inicia em manual. Para controlar pelo teclado, em outro terminal **do mesmo contêiner**:

```bash
docker exec -it robo_movel_navegacao bash -c 'source /opt/ros/jazzy/setup.bash; source /work/install/setup.bash; ros2 run teleoperacao teclado --ros-args -p use_sim_time:=true -r /cmd_vel:=/cmd_vel_manual'
```

No ambiente ROS desse mesmo contêiner, selecione autônomo e envie objetivo novo, em coordenadas do mapa:

```bash
ros2 service call /arbitro/automatico std_srvs/srv/SetBool '{data: true}'
ros2 run navegacao_autonoma ir_para --x .6 --y .15 --yaw 0
```

O cliente não seleciona/rearma o modo automaticamente. Os comandos devem ser executados após o mapa/TF/costmaps estarem prontos. O mapa inicial é parcial; objetivos em região desconhecida ou ocupada podem ser recusados/abortados. Construa o mapa por condução manual em área livre quando necessário.

Tomar controle manual ou travar parada:

```bash
ros2 service call /arbitro/automatico std_srvs/srv/SetBool '{data: false}'
ros2 service call /arbitro/parar std_srvs/srv/Trigger '{}'
```

A proteção da nova composição cancela objetivos upstream ao perder autoridade e recusa comandos/objetivos antigos no rearme. Perda dos dados necessários trava parada; recuperar sensor não é autorização para retomar movimento. Os ensaios registram latências e deslocamentos observados, não garantias de parada elétrica.

## Persistência e localização

O salvador nativo do recorte SLAM continua disponível. Salve mapa e grafo com prefixo novo:

```bash
ros2 run mapeamento_slam salvar_mapa --arquivo /mapas/sala
```

Depois de encerrar a composição, use o grafo persistente:

```bash
bash docs/navegacao/iniciar-conteiner.sh localizacao /mapas/sala
```

PGM/YAML não substituem `.posegraph`/`.data` para o modo localização do SLAM Toolbox. Compatibilidade de serialização/ARM64 exige ensaio no destino. Leia também o guia de SLAM, sem confundir sua entrega anterior com a validação desta integração.

## Reproduzir a validação

```bash
bash docs/navegacao/validar-conteiner.sh /caminho/absoluto/novo
```

O runtime usa imagem `robo-movel/navegacao:jazzy`, fonte somente leitura e diretório separado para build/instalação/resultados. Dependências são instaladas no build da imagem, não no runtime. O cenário possui paredes para raios, mas **a planta não impede contato**: o oráculo audita a trajetória verdadeira e a envoltória conservadora, incluindo os trechos entre amostras. Contato detectado reprova o ensaio, não é escondido por um simulador que permite atravessar paredes.

Não autoriza hardware, deployment, GPIO, serial, impressão, commit ou push. Não certifica segurança física nem autentica publicadores ROS. Manual não ganha prevenção de colisões implicitamente. Os CADs e capturas derivados mantêm as pendências de licença registradas no projeto.

## Inicialização e diagnóstico

O lifecycle de SLAM/salvador é gerenciado por `lifecycle_slam_navegacao`. `lifecycle_navegacao` não usa autostart: um inicializador de execução única aguarda mapa, scan, odometria e TF prontos, solicita STARTUP e verifica sua resposta. Sem prontidão em 30 s ou com falha do STARTUP, a composição encerra; não há sleep fixo mascarando dependências. O árbitro permanece manual.

`/navegacao/estado` é JSON/String retido. Depois de selecionar autônomo, aguarde `aceita_objetivo=true` da mesma `geracao`: o cancelamento preventivo precisa ser confirmado antes da aceitação de um objetivo novo. O CLI público já faz essa espera; no RViz, selecione autônomo, confira o estado e só então use a ferramenta Nav2 Goal.

Scan, odometria e TF são verificados em tempo ROS e monotônico, com prazo padrão 0,5 s; a TF pode estar até 0,25 s no futuro e o comando até 0,05 s. Comando tem prazo de 0,3 s. Repetir carimbo de sensor/comando não renova sua validade. O mapa é exigido válido, mas não periódico, pois localização também pode usar mapa estático. A confirmação de cancelamento cria uma cerca temporal; objetivo anterior não é reautorizado só por trocar de modo.

As latências de falha medidas são resultados deste contêiner, não limites certificados. A suspensão de `/clock` congela a própria planta no ensaio, portanto seu deslocamento nulo não comprova frenagem física.

## Candidato DWB preservado

O candidato DWB carregava plugins e movia a base, mas apresentou mínimos de custo discretos e voltas desnecessárias. A avaliação real de trajetórias mostrou parada preferida pelos críticos de alinhamento. Um ajuste concluiu o primeiro desvio, mas o segundo excedeu o orçamento do ensaio. Foi substituído por RPP, sem alterar margem de colisão, tolerâncias de objetivo, watchdogs ou orçamento de 100 s por objetivo. A configuração anterior fica em `candidatos/`; não é a configuração de execução atual.

## Alteração restrita na camada de rodas

O SDK Jazzy apresentou corridas de shutdown em `take_message`, no construtor do executor e em consulta de TF. Os adaptadores afetados usam sinais que marcam intenção de saída, sem injetar KeyboardInterrupt dentro das conversões C++/pybind11; o laço retorna por spin_once limitado. A assinatura RuntimeError conhecida só é tratada com contexto já inválido; os testes negativos preservam propagação de erros ativos ou diferentes. Foram afetados o diagnóstico de trajetórias, o LiDAR virtual, a camada de rodas e a proteção nova. Cinemática, limites e leases não foram alterados.

## Encerrar corretamente

No helper público, Ctrl+C executa parada e SHUTDOWN dos lifecycle managers, lê de volta os seis estados `finalized` e só então sinaliza o launch. A sessão filha é isolada com setsid e restaura SIGINT/SIGTERM ignorados por jobs em background. Esse caminho foi exercitado por PTY real, com saída zero e remoção do contêiner.

Ao usar `ros2 launch` diretamente, em outro terminal **do mesmo ambiente ROS**, primeiro execute:

```bash
ros2 run navegacao_autonoma encerrar
```

Depois do retorno confirmado, feche RViz e encerre o launch. **SIGINT direto no SLAM Toolbox ativo pode abortar uma thread de TF upstream**; não é o caminho de encerramento aprovado. O comando acima para e encerra software, não substitui E-stop físico.

## Resultado final consolidado

503 casos dos doze pacotes + 10 do oráculo/helpers = **513 casos**, sem erros, falhas ou ignorados; wrapper CTest e repetições não foram somados. Três objetivos reais concluíram SUCCEEDED. Cancelamento, tomada manual, perdas de dados, objetivo fora do mapa, reinício, recarga do grafo e RViz estão documentados no relatório.

A execução final mediu erro real máximo de 10,17 cm nos três objetivos. São métricas de cenário sintético, não precisão do robô físico. A captura do RViz foi inspecionada: Global Status Ok e caminho visível; erro GLSL inicial Ogre/Mesa e sobreposições gráficas permanecem registrados, sem atribuição de causa não investigada.

## Arquivo de atualização

[ZIP da atualização Nav2](robo-movel-nav2-atualizacao-v1.zip) · [Escopo e aplicação](ENTREGA-ATUALIZACAO.md). Exige o workspace anterior; não é instalação independente.
