# Responsabilidades das pastas

## Organização implementada

Existem somente os agrupadores `src/{descricao,localizacao,dispositivos,navegacao,percepcao}`, sem `package.xml` neles. Os doze pacotes concretos ficam dentro; não existe sexto domínio de interfaces, controle ou mapeamento.

- `descricao/robo_movel`: URDF, malhas, configuração RViz e RSP. Não adquire sensores nem publica odometria.
- `dispositivos/simulador_base`: planta cinemática, encoders/IMU virtuais, `/clock`, referência perfeita de ensaio e contrato próprio `msg/LeituraRodas.msg`.
- `dispositivos/lidar_simulado`: raycasting do cenário 2D, extrínseca virtual fixa e `/scan`. Referência perfeita é usada apenas para gerar raios; não publica mapa ou posição medida.
- `localizacao/odometria_rodas`: integra contagens em odometria local e estados de juntas.
- `localizacao/fusao_sensores`: configuração/launch do EKF robot_localization, dono de `odom -> base_footprint`.
- `localizacao/mapeamento_slam`: configuração/composição do SLAM Toolbox, dono de `map -> odom`, persistência de ocupação via servidor nativo dedicado/grafo via serviço do SLAM e localização sobre grafo salvo. Não reimplementa SLAM.
- `percepcao/processamento_imu`: valida e trata amostras sintéticas/inerciais recebidas; não cria aquisição I²C concorrente na Raspberry.
- `navegacao/comando_rodas`: cinemática inversa de TwistStamped para referências de rodas, com validade temporal. Não é o PI/PID do ESP.
- `navegacao/teleoperacao`: teclado/deadman/expiração, sem objetivos autônomos.
- `navegacao/navegacao_simulada`: composição do recorte local, parâmetros didáticos e trajetórias diagnósticas; o nome não implica navegação autônoma.

- `navegacao/arbitro`: seleciona comandos manuais/autônomos por modo explícito e publica /cmd_vel; não é coordenador de ações nem planejador. [Contrato](arbitro/LEIA-ME.md).

## Interfaces

Cada contrato próprio pertence ao pacote que o produz (`msg/`, `srv/`, `action/` quando necessários). Consumidores importam esse dono, sem cópias ou pacote central. Usar tipos padrão quando suficientes: LaserScan, Odometry, Imu, JointState e TwistStamped. Os serviços de persistência são os tipos do SLAM Toolbox, não novas cópias locais.

O produtor virtual possui sua mensagem de rodas; isso não define um protocolo UART físico. Interfaces ROSIDL precisam de ament_cmake e instalação compatível com os nós Python; essa combinação foi exercitada no simulador.

## Recursos e documentação

Recursos executáveis ficam nos pacotes proprietários: `inicializacao/`, `configuracao/`, `visualizacao/`, `descricao/` e `recursos/` conforme uso real. O índice instalado preserva a convenção ament. Documentação acadêmica, procedimentos, fontes e evidências ficam em `docs/`, não como manuais nos módulos.

Mapas salvos são dados mutáveis de sessão, fora do share instalado. O helper SLAM monta `/mapas` persistente; relatórios e amostras de ensaio podem ser arquivados sob `docs/slam/`. Não salvar resultados no código/recursos somente leitura.

## Hardware e navegação ainda não implementados

A futura ponte `dispositivos/comunicacao_esp` deverá ser o único dono da UART bidirecional, transmitindo referências e recebendo encoders/IMU. Aquisição e PI/PID de rodas permanecem no ESP. O futuro pacote C1 reutilizará um driver existente após confirmar interface/montagem; o LiDAR virtual não é esse driver.

Planejamento/seguimento autônomos futuros pertencem a `navegacao`, preferindo Nav2 em vez de duplicá-lo. Filtros/percepção adicionais só quando houver necessidade medida. Não criar caminhos concorrentes de controle/TF por organização de diretórios.

Veja [arquitetura](02-arquitetura.md), [simulação local](simulacao/LEIA-ME.md), [SLAM](slam/LEIA-ME.md) e [UART proposta](04-comunicacao-uart.md). Nenhum ensaio virtual autoriza hardware/deploy.

## Integração de navegação virtual

`navegacao/navegacao_autonoma` compõe Nav2 (NavFn + Regulated Pure Pursuit), costmaps e proteção de autoridade/dados. [Operação, validação e limites](navegacao/LEIA-ME.md). O árbitro continua único publicador da saída final; a integração cancela objetivos ao tomar controle manual e trava parada na perda dos dados necessários. Nenhum hardware foi acionado.
