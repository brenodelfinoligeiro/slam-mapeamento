# 6. Validação e calibração

## Separar resultado e procedimento

Cada registro deve distinguir o que foi executado do que está proposto. Para um ensaio físico, informar componente, versão do programa, alimentação, instrumento, condição de carga, configuração e arquivo de evidência.

A compilação do pacote e testes de estrutura não validam hardware, navegação ou qualidade da odometria.

## Evidências de software disponíveis

A estrutura inicial foi reconhecida por colcon, compilada, instalada e importada fora da árvore fonte. A localização em português foi validada com dois testes. O relatório daquele estado foi preservado no histórico.

A centralização atual acrescenta um teste de separação entre documentação e código e exige reconstrução limpa da instalação. Os resultados dessa etapa devem ser consultados em [validacao-centralizacao.md](validacao-centralizacao.md), não inferidos dos testes anteriores.

## Integração virtual executada

A [simulação local](simulacao/LEIA-ME.md) exercita encoders/IMU/EKF/teleop. A [extensão SLAM](slam/LEIA-ME.md) acrescenta mundo 2D, LaserScan, mapa aprendido, TF global, salvamento e nova execução em localização sobre grafo. Esses fluxos usam ROS/DDS real e referência perfeita separada apenas como oráculo/geração de sensores, não como medição global fornecida ao estimador.

Validar algoritmo/configuração em cenário sintético não prova precisão física, calibração, dinâmica/contato ou navegação. Não somar wrappers CTest aos casos pytest subjacentes; conferir contagens e XML por pacote.

## Ensaios físicos ainda não executados

### Mecânica e codificadores

Conferir fixação do motor, folga do disco, alinhamento do sensor e contagens por volta completa da roda. Repetir a medição para verificar consistência. Registrar a convenção de contagem de bordas.

### Alimentação e ponte

Confirmar tensão admissível dos motores, alimentação e jumpers do módulo L298N. Iniciar em bancada com fonte limitada e sem prolongar bloqueio do eixo. Verificar desabilitação na inicialização, sentido de cada canal, resposta ao PWM e reversão após comando zero. Medir tensão nos motores, corrente de partida e aquecimento do módulo; observar se a queda de tensão impede a partida ou reduz o desempenho.

### Controle das rodas

Testar uma roda suspensa por vez. Medir referências, velocidades estimadas, comando aplicado, corrente quando disponível e comportamento de reversão. Ajustar PI a partir de dados, não pela aparência do movimento sem carga. Só então testar ambas as rodas e o protótipo lentamente no chão.

### IMU

Confirmar níveis lógicos e eixos. Medir o desvio do giroscópio em repouso, a variação do ruído e a influência da montagem. Registrar a configuração das faixas e filtros. Não tratar rumo integrado como referência absoluta.

### LiDAR e referências

Confirmar a comunicação e representar a varredura em uma referência identificada. Medir a posição do sensor no robô, verificar o sentido da varredura e conferir a coerência no RViz. Não escolher uma transformação apenas para alinhar visualmente um mapa.

### Odometria e localização

Medir diâmetro efetivo das rodas e distância entre elas. Comparar deslocamentos e giros com uma referência externa. Incluir reversões e movimentos que tornem o sinal inferido dos codificadores incerto. Ajustar geometria e covariâncias sem esconder patinagem ou baixa resolução.

### Mapeamento e navegação

Salvar somente mapas realmente produzidos e identificar condições do ambiente. Antes de afirmar navegação funcional, verificar objetivos, comandos, localização e trajeto observado no protótipo.

## Organização das evidências

Manter relatórios, gráficos e capturas em `docs/anexos/` ou em subpastas de ensaio sob `docs/`. Arquivos volumosos podem ficar em armazenamento apropriado, referenciados pelo relatório com identificação verificável. Não misturar dados brutos ou relatos de experimento nos módulos Python.

## Integração de navegação virtual

`navegacao/navegacao_autonoma` compõe Nav2 (NavFn + Regulated Pure Pursuit), costmaps e proteção de autoridade/dados. [Operação, validação e limites](navegacao/LEIA-ME.md). O árbitro continua único publicador da saída final; a integração cancela objetivos ao tomar controle manual e trava parada na perda dos dados necessários. Nenhum hardware foi acionado.
