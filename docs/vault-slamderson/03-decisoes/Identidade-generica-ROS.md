# Identidade genérica do software ROS

## Decisão do autor

O apelido afetivo do carrinho não deve identificar o projeto ROS. Usar `robo_movel` para a base existente e `/home/lamggm/projects/robo_movel_ws` como workspace canônico. Código próprio segue em pt-BR; APIs e convenções ROS externas permanecem intactas.

## Alteração realizada

Pacote Python/ament, recursos, URDF, URIs das malhas, launches e RViz usam a identidade genérica. Duas regressões impedem o retorno do apelido ao código/recursos ROS. O caminho antigo do workspace é apenas um alias de compatibilidade. `AGENTS.md` foi preservado; sua referência antiga ao pacote é histórica, e os comandos atuais estão em `docs/05-desenvolvimento-e-execucao.md`.

Originais CAD/STL, histórico Git e recibos anteriores não foram rebatizados nem reescritos. A procedência do CAD continua resolvida por registro externo ao pacote, com hash; as malhas de runtime não foram modificadas.

## Organização vigente — recorte de simulação implementado

O autor definiu apenas os agrupadores `descricao`, `localizacao`, `dispositivos`, `navegacao` e `percepcao` em `src/`, com pacotes ROS concretos dentro deles. Agrupadores não possuem `package.xml`. A proposta anterior de pacotes irmãos prefixados foi substituída.

- `descricao/robo_movel`: descrição existente, movida preservando identidade e recursos.
- `localizacao/odometria_rodas` e `localizacao/fusao_sensores`: odometria e estimativa local.
- `dispositivos/comunicacao_esp` e `dispositivos/lidar_c1`: aquisição/comunicação, cada pacote dono de seus contratos específicos.
- `navegacao/comando_rodas`: referências de velocidade das rodas; planejamento/seguimento futuros neste domínio.
- `percepcao/processamento_imu`: tratamento inercial recebido do ESP, sem aquisição I²C duplicada na Pi.

SLAM/mapeamento implementado em `localizacao/mapeamento_slam`; controle de movimento a `navegacao`. Não criar agrupadores-raiz adicionais `mapeamento`, `controle` ou `interfaces`. A descrição foi movida para `src/descricao/robo_movel/`. O recorte de simulação está implementado; ponte ESP e C1 reais permanecem propostos.

## Propriedade das interfaces

O autor rejeitou um pacote central de interfaces. Contratos próprios ficam no pacote proprietário, em `msg/`, `srv/` e/ou `action/`, conforme necessidade. Consumidores dependem do proprietário e reutilizam o mesmo tipo, sem duplicá-lo. Mensagens padronizadas de IMU, odometria e LiDAR continuam preferidas quando suficientes.

A ponte pode definir seus tipos de comando, leitura de rodas e amostra inercial; odometria, comandos e processamento IMU os consomem. Alterar um contrato ainda pode exigir reconstruir/ajustar consumidores. Evitar dependências circulares.

Geração ROSIDL exige `ament_cmake`, não `ament_python` puro. A documentação Jazzy alerta para a incompatibilidade de `rosidl_generate_interfaces` com `ament_python_install_package` no mesmo projeto. Uma instalação Python alternativa no pacote proprietário precisa ser exercitada antes de adotada; não mudar os nós para C++ silenciosamente nem apresentar essa escolha como build já validado. Fonte e procedimento constam no plano. Essa ressalva descrevia a proposta inicial; o produtor de interfaces virtual foi implementado e exercitado posteriormente no recorte de simulação, sem definir UART real.

## Verificação

Build/instalação, 18 testes colcon, URDF, TFs e RViz exercitados em contêiner ROS 2 Jazzy isolado. Não houve push, deploy, UART ou acionamento de hardware. A distribuição final da Pi, o firmware e o protocolo continuam pendentes.

Relacionados: [[03-decisoes/Arquitetura-atual]], [[04-experimentos/Descricao-ROS-R05]], [[Inicio]]. Plano detalhado em `docs/planejamento/`; resultados em `docs/descricao-ros/`.

## Recorte de simulação

[[04-experimentos/Simulacao-odometria-IMU-teleop]] registra a execução real em contêiner Jazzy. O produtor virtual possui seu próprio `msg/LeituraRodas.msg`; demais saídas usam tipos ROS padronizados. Não confundir a interface do simulador com protocolo UART implementado ou pronto para hardware.

## Extensão com SLAM

`dispositivos/lidar_simulado` e `localizacao/mapeamento_slam` completam o recorte atual de dez pacotes, sem sexto agrupador. Usam LaserScan/OccupancyGrid e serviços upstream, não duplicam tipos. [[04-experimentos/SLAM-virtual-e-localizacao]].
