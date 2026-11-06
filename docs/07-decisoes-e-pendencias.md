# 7. Decisões e pendências

## Decisões confirmadas

- Projeto acadêmico em português brasileiro.
- Documentação detalhada exclusivamente em `docs/`, fora da árvore fonte.
- Identidade ROS genérica; pacote de descrição `robo_movel` e pacotes funcionais nos cinco agrupadores sem manifesto, com interfaces próprias por produtor.
- Desenvolvimento local no Xeon e Raspberry Pi 5 de 8 GB prevista para processamento embarcado.
- Comunicação direta UART entre Raspberry e ESP.
- Dados dos codificadores e da MPU-6050 recebidos do ESP pela mesma UART.
- Controle PI das rodas mantido no ESP.
- Identificação dos módulos dos codificadores confirmada pelo autor: `mh-sensor-series` (inscrição observada: `MH-Sensor-Series`). Pinagem, alimentação, nível de saída e resolução ainda precisam ser verificados.
- LiDAR C1 incluído no projeto.
- Módulo de ponte H dupla L298N para os motores, sem desenvolvimento de placa de acionamento nesta etapa.
- Escopo de protótipo didático, com cuidados proporcionais e sem infraestrutura industrial desnecessária.
- Quatro pilhas AA nesta etapa, com powerbank separado para a Raspberry. [Estudo de disposição 2D](disposicao-2d/LEIA-ME.md) disponível; posições, suportes e desempenho elétrico ainda não aprovados.

## Recomendações ainda não confirmadas

- Considerar ESP32 clássico se o contador PCNT facilitar a leitura dos codificadores. O C3 continua viável com interrupções e PWM LEDC; MCPWM não é requisito da L298N. A placa final ainda não foi escolhida.
- `robot_localization` e SLAM Toolbox já foram integrados na simulação. Nav2 permanece recomendação para a próxima etapa de navegação, ainda não implementada.

## Informações ainda necessárias

1. Placa ESP final e pinos disponíveis.
2. Química e holder das quatro AA; alimentação da lógica e validação dos motores informados como 12 V com 6 V nominais (se alcalinas), antes das perdas na L298N.
3. Caracterização dos motores reais e resolução dos codificadores.
4. Pinagem e níveis das placas dos sensores.
5. Modelo do módulo L298N, alimentação lógica, jumpers e verificação de corrente, queda de tensão e temperatura com os motores reais.
6. Interface, controlador e montagem do LiDAR C1.
7. Distribuição ROS 2 e ambiente de execução.
8. Protocolo UART, unidades, marcas temporais e frequências de comunicação.
9. Geometria medida do robô e dos sensores.
10. Licença e contato de manutenção.

## Próximas etapas

O autor pediu SLAM/localização antes de navegação: o recorte virtual já tem odo/IMU/EKF, LiDAR virtual, mapa e recarga por grafo. A próxima etapa de software é navegação, mediante novo pedido; hardware continua exigindo firmware/ponte UART, C1 real, calibrações e ensaios próprios.

A ordem pode ser ajustada pelos resultados. A existência de uma pasta de percepção não obriga criar um algoritmo de percepção adicional antes de observar uma necessidade.

## Regra de manutenção

Uma alteração que mude responsabilidades, interfaces, parâmetros ou procedimentos deve atualizar o capítulo correspondente em `docs/`. No código ficam somente comentários locais necessários e documentação curta de interface; justificativas, tutoriais, experimentos e histórico ficam nesta documentação central.

## Integração de navegação virtual

`navegacao/navegacao_autonoma` compõe Nav2 (NavFn + Regulated Pure Pursuit), costmaps e proteção de autoridade/dados. [Operação, validação e limites](navegacao/LEIA-ME.md). O árbitro continua único publicador da saída final; a integração cancela objetivos ao tomar controle manual e trava parada na perda dos dados necessários. Nenhum hardware foi acionado.
