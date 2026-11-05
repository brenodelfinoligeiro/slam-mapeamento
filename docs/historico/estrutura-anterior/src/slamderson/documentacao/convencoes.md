# Convenções de idioma e organização acadêmica

## Idioma do projeto

O Slamderson é um trabalho acadêmico localizado em **português brasileiro**. Utilizar português nas pastas próprias, variáveis próprias, funções próprias, comentários, documentação e mensagens produzidas pelo projeto.

- Textos em UTF-8, com acentuação normal.
- Pastas e identificadores de código em português sem acentos, em letras minúsculas e com sublinhado quando necessário: `navegacao`, `localizacao`, `dispositivos`, `percepcao`, `mapeamento`, `controle`.
- Arquivos de apresentação chamados `LEIA-ME.md`.
- Redação técnica e adequada ao contexto acadêmico, sem informalidade ou afirmações não verificadas.
- Distinguir proposta, componente informado, resultado medido e funcionalidade implementada.

## Identificadores externos preservados

Não traduzir nomes exigidos por padrões ou ferramentas: `package.xml`, `setup.py`, `setup.cfg`, `__init__.py`, `.gitignore`, chaves de metadados do setuptools/pytest, dependências e comandos externos. Diretórios gerados `build/`, `install/` e `log/` permanecem gerenciados pelo colcon.

O pacote continua se chamando `slamderson`; a raiz da área de trabalho mantém o sufixo convencional `_ws`. UART, I²C, ESP32, MPU-6050, LiDAR, ROS 2, Nav2 e nomes de algoritmos permanecem siglas ou nomes próprios.

Tipos de mensagem e identificadores usados na integração com pacotes externos, como `sensor_msgs/Imu`, `sensor_msgs/LaserScan`, `cmd_vel`, `odom` e `base_link`, não devem ser traduzidos de modo a quebrar contratos. Quando uma interface própria for criada, preferir nomes em português e documentar qualquer correspondência necessária com interfaces externas.

A coleta do pytest foi configurada para `testes/teste_*.py` e funções `teste_*`. Não é necessário manter nomes próprios de testes em inglês.

## Organização e limites

`inicializacao/`, `configuracao/`, `descricao/`, `mapas/`, `visualizacao/` e `documentacao/` contêm recursos do pacote. `recursos/slamderson` fornece o marcador ament, instalado no caminho padronizado do índice ROS.

Nenhum arquivo reservado representa uma funcionalidade em execução. Manter a aquisição da MPU-6050 no ESP, sua telemetria pela UART e o PI de velocidade no ESP, sem criar uma segunda interface física apenas por existir uma pasta.
