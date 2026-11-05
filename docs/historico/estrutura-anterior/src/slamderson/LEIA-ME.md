# Slamderson

Estrutura inicial de **um pacote ROS 2 `ament_python`**, destinada a um trabalho acadêmico. Documentação, nomes próprios dos módulos, comentários e mensagens são escritos em português brasileiro. Os diretórios e identificadores próprios usam português sem acentos; os textos usam acentuação normal.

Ainda não existem nós, interfaces de hardware ou arquivos de inicialização implementados.

## Plataforma

- Desenvolvimento no Xeon; processamento embarcado previsto na Raspberry Pi 5, com 8 GB.
- ESP32: controle local das rodas, leitura dos codificadores de rotação e aquisição da MPU-6050.
- UART bidirecional: comandos da Raspberry para o ESP; dados das rodas e da IMU do ESP para a Raspberry.
- LiDAR C1 informado pelo usuário; interface, controlador de dispositivo e montagem a definir.
- Motores TT e módulo L298N; alimentação, jumpers e desempenho com os motores reais ainda precisam ser verificados. Este item foi atualizado para a decisão vigente.

## Organização

```text
slamderson/
  navegacao/
  localizacao/
  dispositivos/
    esp32_uart/
    mpu6050/
    lidar_c1/
  percepcao/
  mapeamento/
  controle/
inicializacao/
configuracao/
descricao/
mapas/
visualizacao/
documentacao/
recursos/
testes/
```

As pastas reservam responsabilidades futuras. Não foram presumidos taxa de transmissão, pinos GPIO, controlador do LiDAR, sistemas de referência ou calibrações. A distribuição ROS 2 também não foi selecionada.

A MPU-6050 é lida pelo ESP e seus dados retornam na mesma UART dos codificadores. `dispositivos/mpu6050/` não representa uma segunda ligação I²C ou uma segunda porta serial na Raspberry.

## Compilar e testar

Na raiz da área de trabalho, com as ferramentas disponíveis:

```bash
colcon list
colcon build --packages-select slamderson
colcon test --packages-select slamderson
colcon test-result --verbose
source install/setup.bash
```

Em uma instalação completa do ROS 2, também será possível consultar `ros2 pkg prefix slamderson`. Esse comando não foi validado sem o ambiente ROS 2. Não existem executáveis próprios para `ros2 run` ou arquivos próprios para `ros2 launch` nesta etapa.

## Convenções e documentação

- [Responsabilidades das pastas](documentacao/responsabilidades.md).
- [Convenções de idioma](documentacao/convencoes.md).
- [Arquitetura inicial](documentacao/LEIA-ME.md).

Nomes padronizados pelo ROS 2, Python e ferramentas externas, como `package.xml`, `setup.py`, `setup.cfg`, `__init__.py`, `ament_python` e as chaves de configuração dessas ferramentas, são preservados. O nome do pacote continua sendo `slamderson`.

## Metadados pendentes

`a_definir@example.com` é um endereço ilustrativo, não um contato confirmado. A licença está como **A definir**; nenhuma licença foi escolhida em nome do autor.

Para as ligações atuais, consultar o [capítulo de componentes](../../../../03-componentes-e-ligacoes.md). O código deste projeto é independente do GREENBOT.
