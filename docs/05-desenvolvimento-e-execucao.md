# 5. Desenvolvimento e execução

## Caminhos e estrutura

Raiz da área de trabalho: `/home/lamggm/projects/robo_movel_ws`.

- `docs/`: documentação acadêmica, procedimentos, decisões e evidências.
- `src/{descricao,localizacao,dispositivos,navegacao,percepcao}/`: agrupadores sem manifesto; doze pacotes ROS internos, incluindo descrição, simulação, sensores, EKF, teleop e SLAM.
- `requisitos-desenvolvimento.txt`: versões das ferramentas utilizadas no empacotamento.
- `build/`, `install/` e `log/`: resultados gerados pelo colcon, não fontes de documentação.

O nome `docs/` foi mantido por solicitação explícita do autor. Seu conteúdo é em português. Os demais diretórios próprios permanecem localizados.

## Execução atual

O runtime completo foi exercitado em contêiner ROS 2 Jazzy no Xeon, sem rede/dispositivos e com fonte somente leitura. Use [SLAM/localização por grafo](slam/LEIA-ME.md) ou o [recorte de odo/IMU/teleop](simulacao/LEIA-ME.md). O host não recebeu ROS nativo; o ambiente Python abaixo serve ao empacotamento, não substitui dependências ROS.

## Preparação isolada das ferramentas

```bash
cd /home/lamggm/projects/robo_movel_ws
uv venv .venv
uv pip install --python .venv/bin/python -r requisitos-desenvolvimento.txt
source .venv/bin/activate
```

Isso prepara ferramentas de empacotamento e teste. Não instala uma distribuição ROS 2 completa. A validação anterior utilizou um ambiente temporário em `/home/lamggm/.hermes/cache/scratch/slamderson-tools`; não depender desse cache como instalação permanente.

## Compilação e testes

```bash
colcon list
colcon build
colcon test --return-code-on-test-failure
colcon test-result --verbose
source install/setup.bash
```

Em zsh, usar `source install/setup.zsh`. Os pacotes são reconhecidos como `ros.ament_python`, exceto o produtor de interfaces `simulador_base`, que usa `ros.ament_cmake`. Os testes usam arquivos `testes/teste_*.py` e funções `teste_*`, configurados em `setup.cfg`.

Após mudanças na organização, verificar importações a partir de `install/` fora da pasta fonte. Conferir também a ausência de módulos antigos que possam permanecer em instalações incrementais.

## Instalação dos recursos

`setup.py` instala o manifesto, o marcador ament e os recursos das pastas `inicializacao`, `configuracao`, `descricao`, `mapas` e `visualizacao`. As pastas agora incluem URDF/malhas, geometria CAD, launches e configuração RViz; os demais recursos ainda podem conter apenas `.gitkeep`.

A documentação de `docs/` não faz parte dos módulos Python nem é instalada como recurso de execução. Não acrescentar cópias de manuais aos diretórios de código para que apareçam no pacote.

## Descrição e visualização implementadas

Em um ambiente com ROS 2 carregado, após compilar e carregar a instalação:

```bash
ros2 launch robo_movel visualizar.launch.py
ros2 launch robo_movel descricao.launch.py
```

O primeiro é demonstração com RViz e juntas de exemplo; o segundo só publica a descrição/TFs e aguarda estados reais das rodas. [Procedimento e limites](descricao-ros/LEIA-ME.md). Não há nós próprios de hardware registrados em `ros2 run`.

A validação nova utilizou ROS 2 Jazzy em contêiner isolado, com instalação, `check_urdf`, 16 testes e TFs reais de mensagens de ensaio. ROS nativo continua ausente no host, e a distribuição alvo da Raspberry não foi escolhida por este teste.

Ao usar fonte fora do workspace de build, passe o mesmo `--base-paths` também ao `colcon test` e confira contagem não nula no XML. Um `test-result` bem-sucedido com zero testes não constitui aprovação.

Não foram assumidos portas de dispositivos, taxa serial, versão de controlador C1 ou acesso remoto à Raspberry. Essas informações serão registradas quando forem medidas ou configuradas.

## Metadados

Nome do pacote: `robo_movel`. A licença e o contato de manutenção continuam pendentes; `a_definir@example.com` é apenas um endereço ilustrativo. Não atribuir licença ou autoria institucional sem decisão do autor.

## Integração de navegação virtual

`navegacao/navegacao_autonoma` compõe Nav2 (NavFn + Regulated Pure Pursuit), costmaps e proteção de autoridade/dados. [Operação, validação e limites](navegacao/LEIA-ME.md). O árbitro continua único publicador da saída final; a integração cancela objetivos ao tomar controle manual e trava parada na perda dos dados necessários. Nenhum hardware foi acionado.
