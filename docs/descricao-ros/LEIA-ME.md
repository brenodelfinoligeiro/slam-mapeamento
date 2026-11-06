# Descrição ROS 2 derivada da montagem R05

## Entrega e limite

`src/descricao/robo_movel/descricao/robo_movel.urdf` foi gerado da montagem nativa **R05**, não dos STL orientados/normalizados para impressão. Inclui as **44 instâncias impressas**, ferragens, chassi, motores, rodas/cubos, discos ilustrativos, rodízio, Pi, L298N, MPU, C1 e envelopes de ESP/holder/Basike. O cupom P25 e os compostos de agrupamento não são exportados como peças duplicadas.

São **7 links, 6 juntas (duas contínuas) e 18 malhas**. A procedência, posições CAD, hashes e simplificação visual estão em `src/descricao/robo_movel/descricao/origem-cad.json`. Os detalhes gráficos foram reduzidos para 660216 triângulos; a verificação de erro registrada é de **caixa envolvente**, não um limite de erro em cada ponto da superfície. Geometria CAD/STL de fabricação permanece inalterada.

**Não é modelo dinâmico calibrado:** não há massas, inércias, limites de torque/velocidade ou `ros2_control` inventados. Colisões estáticas são malhas de referência; rodas usam cilindros aproximados. Não foi validado para contato/simulação dinâmica no Gazebo. As malhas ROS estão em **metros**: não usar esses STL para imprimir.

## Compilar e visualizar

Em um terminal com ROS 2 e as dependências do `package.xml` disponíveis:

```bash
cd /home/lamggm/projects/robo_movel_ws
colcon build --packages-select robo_movel
source install/setup.bash
ros2 launch robo_movel visualizar.launch.py
```

`visualizar.launch.py` inicia RViz e controles de juntas de exemplo; não é aquisição dos encoders. Para demonstrar sem janela/GUI de juntas:

```bash
ros2 launch robo_movel visualizar.launch.py gui:=false rviz:=false
```

Para o robô real, **sem inventar `/joint_states`**:

```bash
ros2 launch robo_movel descricao.launch.py
```

Essa opção só inicia `robot_state_publisher`. A aquisição real deverá fornecer `sensor_msgs/msg/JointState`, com `left_wheel_joint` e `right_wheel_joint` em radianos. O publisher usa esses estados para atualizar as juntas móveis; as fixas usam `/tf_static`.[2]

O host Arch não recebeu instalação nativa de ROS 2. Build, testes e execução foram exercitados em **ROS 2 Jazzy num contêiner isolado**, sem rede, dispositivos ou motores; isso não decide a distribuição a instalar na Raspberry.

## Árvore e convenção

```text
base_footprint
└── base_link
    ├── left_wheel_link    (continuous, eixo +Y)
    ├── right_wheel_link   (continuous, eixo +Y)
    ├── caster_link        (fixed, visual)
    ├── lidar_mount_link   (fixed, datum mecânico)
    └── imu_mount_link     (fixed, datum mecânico)
```

ROS adota referencial destro, unidades SI e eixos X para frente, Y para a esquerda e Z para cima.[1] No CAD, a frente AA está em −Y. A conversão usada é **(x_ros,y_ros,z_ros)=(-y_cad,+x_cad,z_cad)**, após subtrair a origem e converter mm para m: rotação própria com determinante +1, não reflexão. Assim a roda no lado +X do CAD corresponde à roda esquerda ROS; os rótulos históricos E/D do desenho não definem automaticamente o lado ROS.

A origem `base_link` é o ponto médio dos centros geométricos dos pneus no CAD. `base_footprint` usa a projeção desse ponto no plano inferior dos pneus. O raio vertical e a distância entre rodas em `configuracao/geometria_cad.yaml` são **referências do CAD, não calibração física**. O footprint retangular cobre a pose CAD atual, não movimento varrido do rodízio nem cabos reais.

## Sensores e pendências mecânicas

- `lidar_mount_link`: centro XY do corpo CAD C1, na base z145 mm. **Não é o plano óptico do laser.**
- `imu_mount_link`: ponto médio dos dois furos da MPU, no plano inferior do PCB de referência. Seus eixos são os do modelo ROS, **não eixos calibrados da amostra bruta da IMU**. Não foram publicados aliases `imu_link`/`laser` com extrínsecas fictícias.
- Antes de integrar drivers/EKF/SLAM, medir e configurar a transformação dos frames reais dos sensores para esses datums. A mudança de posição MPU na R05 foi respeitada.
- O rodízio do CAD fica **5,313 mm acima do plano inferior dos pneus**. A discrepância foi mantida e registrada: corrigir o URDF sozinho esconderia a pendência do modelo mecânico. Seu conjunto foi representado fixo para visualização, não como simulação de rolamento/giro.
- ESP, holder, fendas/resolução dos encoders e interfaces físicas continuam pendentes. Não houve UART, motores, sensores, odometria ou SLAM executados.

## Verificação real da identidade genérica

- `colcon list`: pacote `robo_movel` descoberto; build e importação instalada fora da fonte concluídos.
- `check_urdf`: árvore válida, nome do robô `robo_movel`; 18 malhas instaladas verificadas por hash.
- `colcon test`: **18 testes**, zero falhas/erros/skips, conferidos pelo XML. Inclui duas regressões de identidade/ausência do apelido no código e nos recursos ROS.
- Identidade anterior ausente dos imports/índice ament da instalação nova; caches e instalações antigos preservados fora do workspace ativo.
- ROS real: `/robot_description` recebido, rodas sem TF fictícia antes dos estados de teste e TFs conferidas com ângulos positivos/negativos.
- RViz real sob Xvfb/Mesa: display **Robô móvel R05**, Global Status OK; [captura inspecionada](previa-rviz.png). Fechamento pela janela seguido do encerramento do launch foi limpo.
- O ensaio ocorreu em contêiner Jazzy sem rede/hardware, não em ROS nativo ou no robô. Byte-compilação desabilitada e variável antiga de descoberta produziram avisos do ambiente no build/ensaio inicial da migração; não foram falhas de teste nem erros de malhas.
- Ensaios anteriores, incluindo falhas do wrapper Xvfb e do encerramento por SIGINT com a janela aberta, permanecem em `docs/historico/descricao-ros-r05-anterior/`. Esse caminho de SIGINT não foi corrigido/revalidado pela renomeação.

A mudança é de identidade, não de geometria, calibração ou funcionalidade de hardware. Relatório consolidado: `validacao-nomenclatura.json`.

## Regenerar sem tocar nos STL de impressão

```bash
/usr/bin/python docs/descricao-ros/exportar-cad.py PASTA_CACHE
uv run --no-project --with trimesh --with numpy --with fast-simplification --with pyyaml \
  python docs/descricao-ros/gerar-descricao.py PASTA_CACHE
```

FreeCAD deve ser importado antes de Part, com bibliotecas em `/usr/lib/freecad/lib`. A origem/hashes são registrados automaticamente. Os scripts de validação ROS ficam nesta pasta; exigem ROS carregado e não devem ser executados contra um robô real ou uma sessão de produção.

## ZIP de entrega

Arquivo: `robo-movel-descricao-r05.zip`.

O ZIP é um recorte instalável: pacote `src/descricao/robo_movel`, recursos completos e esta documentação. Inclui **9 testes focados na descrição**; os testes documentais preexistentes do workspace não foram duplicados no recorte. A validação anterior com 16 testes permanece no histórico; a revalidação corrente tem 18 testes no workspace completo; os 9 do recorte não são somados a eles. O registro local que resolve o arquivo CAD original, o CAD e os STL de fabricação não acompanham esse ZIP; não são necessários para visualizar, mas são necessários para regenerar as malhas.

## Publicação

As malhas derivadas permanecem **somente locais**, sem push automático, registradas em [malhas-somente-locais.json](malhas-somente-locais.json). O ZIP de entrega inclui recursos para uso privado no projeto, não concede autorização de redistribuição. Uma cópia pública sem essas malhas precisa restaurá-las ou regenerá-las a partir das referências autorizadas antes de executar a visualização e seus testes geométricos.

## Referências verificadas

Os portais ros.org/docs.ros.org devolveram intersticial anti-bot, não documentação. Foram consultados os textos dos repositórios oficiais no GitHub; ver [registro de fontes](fontes.json). A convenção e a interface do publisher são referências externas; coordenadas/folgas derivam do CAD local e os resultados do ensaio, dos comandos realmente executados.

## Sources

[1] https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0103.rst — ROS-REP103
[2] https://raw.githubusercontent.com/ros/robot_state_publisher/jazzy/README.md — ROS-RSP-JAZZY
