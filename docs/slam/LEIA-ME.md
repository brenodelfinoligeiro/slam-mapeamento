# SLAM e localização por grafo na simulação

## Escopo e estado

Esta etapa acrescenta `dispositivos/lidar_simulado` e `localizacao/mapeamento_slam` à simulação cinemática de odo/IMU/teleop. Usa SLAM Toolbox para construir um mapa e estimar a pose global, com opção de localizar sobre um grafo salvo. **Este launch continua sem navegação; a integração adicional está no [guia Nav2](../navegacao/LEIA-ME.md).**

A imagem local `robo-movel/slam:jazzy` contém SLAM Toolbox **2.8.5** e o componente `nav2_map_server` para salvar ocupação por um servidor lifecycle persistente, sem iniciar navegação. Isso não inicia Nav2, AMCL, planejadores ou controladores de navegação. A base `robo-movel/simulacao:jazzy` deve existir; o Dockerfile apenas estende esse ambiente já preparado. Nenhum ROS foi instalado nativamente no host.

**Estado observado:** build/instalação e fluxos ROS/DDS de mapeamento, salvamento e reinício em localização foram executados. RViz real foi capturado e fechou normalmente. O relatório consolidado distingue esses ensaios virtuais de qualquer hardware; a qualidade não é inferida só da existência de um `/map`.

## Fluxo e donos das transformações

```text
Encoders + giroscópio -> odometria/processamento -> EKF -> odom -> base_footprint

Pose virtual + paredes do cenário -> LiDAR virtual -> /scan -> SLAM Toolbox
                                      TF de odometria ------^       |
                                                                   +-> /map
                                                                   +-> map -> odom
```

- EKF permanece responsável por `odom -> base_footprint`.
- SLAM Toolbox é o único responsável por `map -> odom`.
- RSP publica relações geométricas do modelo e juntas das rodas.
- O launch antigo recebe `origem_virtual:=false` nesta composição; não pode continuar publicando `simulacao_mundo -> odom`.
- `simulacao_mundo -> map` identidade é uma **definição da coincidência inicial de coordenadas deste cenário**, útil ao oráculo e à visualização. Não determina a pose do robô nem fornece `map -> odom` perfeito ao estimador.
- `lidar_mount_link -> laser_simulado` identidade define um sensor **virtual** sobre o datum do modelo. Não é calibração óptica/extrínseca do C1 físico.

A pose perfeita de `/simulacao/referencia` é usada pelo LiDAR **para gerar a medição sintética**, como a pose verdadeira de um simulador físico geraria uma imagem/range. Ela não é uma entrada do EKF ou do SLAM. O estimador vê somente os raios e a odometria via TF. O arquivo do mundo é recurso da geração de sensores, não um mapa pronto fornecido ao SLAM.

## Iniciar mapeamento no Xeon

Na raiz do workspace:

```bash
bash docs/slam/iniciar-conteiner.sh
```

Em outro terminal do host, **no mesmo contêiner**:

```bash
docker exec -it robo_movel_slam bash -c 'source /opt/ros/jazzy/setup.bash; source /work/install/setup.bash; ros2 run teleoperacao teclado --ros-args -p use_sim_time:=true'
```

`w/s`: avanço/ré; `a/d`: giro; `e/c`: curvas; espaço: parar; `q`: sair do teclado. Sem novas teclas, a referência expira. Ctrl+C no primeiro terminal encerra a composição. O helper é headless; a visualização de teste usa RViz real em Xvfb separado. Não abrir outra instância com o mesmo nome de contêiner.

**O cenário contém paredes/obstáculos para os raios, não uma física de contato.** A base cinemática não impede atravessar uma parede e não implementa desvio. Mantenha o percurso manual em espaço livre; não interpretar ausência de parada como aprovação de colisão/segurança. A região livre de ensaio fica aproximadamente entre x/y de -0,3 a 1,3 m; o percurso automatizado é só uma sequência de teste, não um navegador.

## Salvar mapa e grafo

Com o robô parado e o mapeamento ativo:

```bash
docker exec robo_movel_slam bash -c 'source /opt/ros/jazzy/setup.bash; source /work/install/setup.bash; ros2 run mapeamento_slam salvar_mapa --arquivo /mapas/sala'
```

O prefixo gera ocupação `.pgm`/`.yaml` e grafo `.posegraph`/`.data`. **Os dois arquivos do grafo são necessários** para o modo localização do SLAM Toolbox; PGM/YAML sozinhos são outro tipo de representação. Reutilizar um prefixo existente não deve apagar silenciosamente um ensaio anterior: escolher nome novo.

O diretório `/mapas` é um bind mount persistente do host, por padrão:

```text
~/.local/share/robo_movel/mapas
```

Os mapas não ficam exclusivamente no filesystem removido pelo `docker --rm` nem no scratch sujeito a limpeza. `ROBO_SLAM_MAPAS` permite escolher outro diretório absoluto do host. O cache/build em `/work` é separado e pode ser regenerado.

## Reiniciar em localização no grafo salvo

Encerre a composição de mapeamento. Depois:

```bash
bash docs/slam/iniciar-conteiner.sh localizacao /mapas/sala
```

O início do simulador e a origem do mapa são conhecidos neste cenário didático. Isso não comprova relocalização global arbitrária após mover um robô físico para posição desconhecida. O modo localização usa o executável próprio `localization_slam_toolbox_node`, não AMCL nem um novo mapeamento vazio.

Para uma nova sessão de mapeamento, encerre e inicie novamente no modo `mapeamento`. Reinício isolado da planta/clock com um SLAM já ativo não é o procedimento de recarga validado aqui; reinicie a composição completa e carregue o grafo quando quiser preservar o mapa.

## Dependências e ambiente ROS preparado

Reconstrução da imagem local, com rede apenas durante o build:

```bash
docker build -t robo-movel/slam:jazzy -f docs/slam/Dockerfile docs/slam
```

O runtime roda sem rede externa, sem dispositivos, sem portas publicadas e com fonte somente leitura. Os dois novos pacotes usam tipos/interfaces upstream; não existe pacote central de interfaces criado para esta etapa.

Em ROS Jazzy com todas as dependências já disponíveis:

```bash
colcon build
source install/setup.bash
ros2 launch mapeamento_slam slam_simulado.launch.py
```

O grafo binário foi projetado para a versão de SLAM instalada no ambiente de ensaio; compatibilidade AMD64/ARM64 e entre versões não deve ser presumida sem recarga real no destino. A implantação na Raspberry Pi e o LiDAR físico permanecem fora desta entrega.

## Validação reproduzível

```bash
bash docs/slam/validar-conteiner.sh /caminho/absoluto/novo-para-ensaio
```

O diretório precisa ser novo; resultados anteriores não são apagados. O script executa build/colcon, regressão da base, trajeto de ensaio, comparação geométrica do mapa aprendido, checagem de fontes/TF, salvamento e nova execução em localização. Os relatórios são produzidos dos resultados reais; não são exemplos preenchidos manualmente.

O oráculo de mapa compara células ocupadas e segmentos conhecidos do cenário, com tolerância em metros. Paredes ocultas podem permanecer desconhecidas; essas métricas não são prova de completude de qualquer ambiente, precisão física, dinâmica ou segurança. A suspensão causal do processo SLAM usada no teste ocorre apenas no namespace isolado de PID do contêiner, com retomada garantida, nunca em hardware.

## Limitações

- LiDAR instantâneo 2D, sem distorção de movimento de um scanner rotativo real, oclusão vertical, refletância ou ruído real do C1.
- Mundo sintético de segmentos, sem Gazebo, dinâmica/contato/escorregamento ou adequação elétrica.
- Geometria e ruídos/covariâncias são referências didáticas, não calibração física.
- Nenhum firmware, UART, GPIO, motor, impressora, deploy, commit ou push é autorizado por estes testes.
- Malhas mecânicas e capturas com elas continuam sujeitas às pendências de procedência/licenciamento já registradas; não publicar o recorte automaticamente.

## Resultados arquivados

[Relatório executado na fonte](validacao-slam.json), [captura RViz inspecionada](previa-slam.png), [ocupação salva](mapas/ensaio.yaml) e [mapa PGM](mapas/ensaio.pgm). O prefixo de grafo de amostra é `docs/slam/mapas/ensaio`, com `.posegraph` e `.data`. Arquivos de evidência/JUnit estão em `evidencias/`.

A contagem atual por pacote e do verificador de mapa consta em `validacao-slam.json`; são casos pytest reais, não wrappers. O total bruto de colcon acrescenta um wrapper CTest, que não é outro caso funcional. Não somar novamente os mesmos casos executados no recorte extraído. Seis cenários negativos ROS/CLI são registrados separadamente.

O helper público foi aberto por TTY real nos dois modos, com teleop por PTY, salvamento em `/mapas`, encerramento e nova leitura do mesmo bind persistente. O mapa sobreviveu à remoção do contêiner.

A inspeção RViz confirmou mapa completo, laser/modelo e Global Status Ok; o processo fechou normalmente pela janela. **Os logs gráficos não são silenciosos:** houve erro GLSL inicial de swatch no Ogre/Mesa e descartes de amostras antigas na inicialização, apesar da renderização posterior correta. A causa do erro GLSL não foi corrigida nem atribuída sem diagnóstico.

O empacotamento privado inclui as fontes e recursos necessários ao runtime, não toda a coleção CAD/PDF histórica. O relatório externo `entrega-slam.json` identifica hash e execução do ZIP; não entra no próprio arquivo para evitar autorreferência.

## Persistência nativa e falhas detectadas na exportação

Uma execução separada detectou timeout de 2 s no salvador iniciado pelo proxy do SLAM Toolbox. O erro foi preservado; não foi resolvido aumentando esse prazo. A composição agora mantém `nav2_map_server/map_saver_server` ativo como `salvador_mapa`, com serviço `/salvador_mapa/save_map`, e desativa o proxy `use_map_saver` no SLAM. `salvar_mapa` usa `slam_toolbox/SerializePoseGraph` para o grafo e `nav2_msgs/SaveMap` para ocupação, com campos explícitos. O segundo retorna **bool**: False não pode ser confundido com o código uint8 zero de sucesso do primeiro. O ensaio exige três gravações nativas consecutivas, além da gravação completa/recarga. A causa de baixo nível do timeout no proxy antigo não foi isolada; não se atribui a ele uma configuração QoS falsa sem evidência.

Um shutdown gráfico também expôs RuntimeError do SDK no take_message da trajetória após SIGINT. O nó diagnóstico trata somente essa assinatura quando o contexto já está inválido; erros com contexto válido e outros RuntimeErrors continuam propagados e têm controles negativos. Não é alteração no controle das rodas.
