# 3. Componentes e ligações

## Critério de evidência

Separar componente informado pelo autor, identificação visual, candidato de catálogo e medição real. As fotografias permitem reconhecer famílias de peças, mas não garantem tensão nominal, corrente, relação de redução ou pinagem.

## Raspberry Pi e ESP

A Raspberry Pi 5 de 8 GB foi confirmada pelo autor. A placa ESP final permanece pendente. O ESP32 clássico oferece PCNT para contagem dos codificadores; o C3 pode usar interrupções de GPIO. O PWM da L298N pode ser gerado por LEDC, sem exigir MCPWM. A seleção depende também dos GPIOs disponíveis na placa escolhida.

A comunicação entre as placas será UART lógica de 3,3 V: TX de uma chega ao RX da outra, com referência GND comum. UART não fornece alimentação. Pinos físicos, porta Linux e taxa de transmissão ainda precisam ser escolhidos no hardware real.

## Motores e leitura óptica

As fotos indicam motorredutores TT amarelos de saída dupla. O autor informa que os motores são de 12 V; essa tensão ainda não foi confirmada por inscrição/datasheet do fabricante. A carcaça do motor é compatível com tamanho 130, mas não há código confirmado. Uma ponta da saída move a roda e a outra recebe o disco óptico.

O autor confirmou a identificação dos módulos dos codificadores como `mh-sensor-series`, correspondente à inscrição `MH-Sensor-Series` observada nas placas. O conjunto observado é óptico incremental, com disco fendido e sensor em garfo. Essa identificação não confirma, por si só, modelo FC-03, uso de comparador LM393, pinagem ou características elétricas. Aparentemente existe um canal por roda; não há evidência suficiente para declarar quadratura A/B.

A pesquisa encontrou uma página comercial que associa MH-Sensor-Series, FC-03 e LM393; essa é uma associação da oferta, não confirmação da revisão dos módulos instalados.[1] Foi obtido um manual Whadda/Velleman WPSE347 para um módulo semelhante, com inconsistências de alimentação e um exemplo incorreto de RPM, explicitados na análise crítica.[2] O datasheet TI do LM393 foi obtido como referência primária do comparador, de aplicação condicional à identificação da placa.[5]

As referências, os arquivos originais disponíveis e as ressalvas estão na [nota dos encoders](vault-slamderson/01-componentes/Encoder-MH-Sensor-Series.md) e no [catálogo bibliográfico](vault-slamderson/05-fontes/Catalogo-de-fontes.md). Não foi encontrado um datasheet primário que identifique inequivocamente a revisão exata dos módulos do carrinho.

Pendências: fixação mecânica, inscrição do motor, tensão admissível, corrente de partida/travamento, contagens por volta da roda, ordem dos pinos, alimentação e nível de saída dos sensores. Uma foto anterior sugeria motor desacoplado; verificar sem assumir quebra.

Valores de um TT comercial semelhante não são dados dos motores instalados. Não dimensionar a ponte pela corrente sem carga e não atribuir a relação 1:48 ao conjunto real sem evidência.

## MPU-6050

Modelo informado pelo autor. Possui acelerômetro e giroscópio de três eixos, sem magnetômetro. A ligação proposta é I²C ao ESP. As amostras seguirão na mesma UART dos codificadores.

A placa de adaptação específica ainda precisa ser inspecionada para confirmar alimentação, regulador e resistores de elevação de SDA/SCL. Não presumir tolerância a 5 V. Calibrar o desvio do giroscópio e medir a orientação física da placa. O rumo integrado deriva no tempo; não corresponde a uma bússola.

## LiDAR C1

O autor incluiu um LiDAR C1 no projeto. Controlador, interface elétrica, adaptador, porta, alimentação, taxa e montagem não foram confirmados. Reservar a integração em `dispositivos/lidar_c1`, sem abrir portas ou inventar configuração.

O controlador deverá representar as varreduras com uma referência coerente e com a posição do sensor descrita no robô.

## Acionamento com módulo L298N

O acionamento adotado nesta etapa é um **módulo L298N de dois canais**, um por motor. O circuito integrado contém duas pontes completas, entradas de direção e habilitação independente dos canais. A placa comercial específica ainda não foi identificada; confirmar suas inscrições e jumpers antes da montagem.

### Ligações funcionais propostas

- Motor esquerdo: saídas `OUT1` e `OUT2`, canal A.
- Motor direito: saídas `OUT3` e `OUT4`, canal B.
- ESP -> `IN1` e `IN2`: direção do motor esquerdo.
- ESP -> `IN3` e `IN4`: direção do motor direito.
- ESP -> `ENA`: PWM do canal A.
- ESP -> `ENB`: PWM do canal B.
- Alimentação dos motores -> entrada de potência do módulo, respeitando o módulo e a tensão admissível dos motores.
- GND do módulo, do ESP e da Raspberry: referência comum, sem fazer a corrente dos motores retornar pelos cabos de sinal.

Essa distribuição reserva quatro saídas digitais e duas saídas PWM no ESP; não define GPIOs físicos. Os nomes dos terminais são os usuais, mas devem ser conferidos na placa real. O sentido físico depende da polaridade dos fios e precisa ser verificado com cada roda suspensa.

Para regular velocidade por `ENA` e `ENB`, remover os jumpers que mantenham essas entradas permanentemente habilitadas, **se existirem na placa adquirida**. Não confundir esses jumpers com o jumper do regulador de alimentação.

O módulo não mede rotação nem executa PI/PID. O ESP continua lendo os codificadores, calculando o controle e aplicando direção e razão cíclica do PWM. A UART e o caminho dos dados da MPU-6050 não mudam.

### Alimentação e limitações

A L298N apresenta queda de tensão relevante no estágio de saída e dissipa calor. A tensão efetiva no motor será menor que a alimentação do módulo e dependerá da corrente. Isso importa especialmente para motores TT de baixa tensão: verificar partida, velocidade e temperatura com a bateria real, sem compensar elevando a tensão acima do que o motor suporta.

A capacidade de corrente contínua depende do módulo, dissipação e condições reais. Não tratar o valor máximo do anúncio como corrente contínua garantida para as duas rodas.

O circuito integrado usa alimentação lógica separada da alimentação de potência. Placas comerciais podem incluir regulador e jumper, com limites próprios: identificar a placa antes de decidir como alimentar seu terminal lógico de 5 V. Não usar esse terminal como fonte para a Raspberry, não conectá-lo a GPIOs do ESP e não unir duas saídas de alimentação de 5 V.

Inicializar o acionamento desabilitado e reduzir o comando a zero antes da reversão. O comportamento de roda livre ou frenagem deve ser escolhido conforme a tabela do componente, não presumido apenas pelo sentido solicitado.

Referência do fabricante: [STMicroelectronics — L298](https://www.st.com/en/motor-drivers/l298.html). Essa referência descreve o circuito integrado; não substitui a identificação do módulo comercial. Não foi realizado ensaio físico com a L298N nesta etapa.

## Alimentação e ensaio inicial

O autor forneceu o [powerbank real Basike](vault-slamderson/01-componentes/Powerbank-Basike.md): envelope informado de 150 × 70 × 30 mm e leitura de 420 g na balança. As fotos do ZIP mostram a etiqueta com saída USB-C e cabo USB-C de 5 V/3 A, e saída total declarada de 15 W; a inscrição frontal 22,5 W não prova 5 V/5 A para a Raspberry. Dados completos, limites da leitura, originais preservados e consequências mecânicas estão na nota. Os estudos 2D/R01 anteriores conservam a reserva antiga de 120 × 65 × 25 mm. A [R02](carcaca-r02/LEIA-ME.md) corrige o Basike para 150 × 70 × 30 mm, em berço baixo traseiro, com nova carcaça ventilada removível; adequação física/térmica continua pendente.

O autor definiu **quatro pilhas AA** para esta etapa, mantendo o powerbank da Raspberry separado. Essa decisão substitui o exemplo anterior de oito alcalinas. Quatro AA alcalinas em série correspondem a 6 V nominais; se forem NiMH, a 4,8 V. A queda das pilhas sob carga e a perda na L298N reduzem a tensão efetiva nos motores informados como 12 V: partida, torque e desempenho não foram validados. Não foi incluído conversor elevador. Química, porta-pilhas, corrente real dos motores, powerbank e alimentação do ESP continuam pendentes; a posição das peças está no [estudo mecânico 2D](disposicao-2d/LEIA-ME.md), sem aprovação de encaixes ou fabricação.

Esse arranjo mantém as fontes dos motores e da Raspberry separadas na primeira montagem. A referência lógica deve ser comum quando não houver isolamento, mas a corrente dos motores não deve retornar pelos fios de sinal. Prender o powerbank temporariamente com uma cinta ou suporte removível, sem cobrir dissipadores, ventoinhas ou conectores, é melhor que deixá-lo solto durante movimento.

A Raspberry Pi recomenda fonte de 5 V/5 A para a Pi 5; uma fonte de 3 A é utilizável com restrições de potência disponível nas portas USB. Portanto, a etiqueta e a saída real do powerbank importam; a capacidade em mAh sozinha não confirma que ele sustente a tensão/corrente exigidas.[23] Não desenhar suporte definitivo nem assumir autonomia até conhecer o powerbank exato e testar a Pi sob a carga planejada.

Deixar o conjunto de pilhas baixo é uma hipótese de montagem; a distribuição proposta precisa de conferência de acesso, retenção, centro de massa e estabilidade. A escolha de quatro AA pelo autor não substitui a medição de tensão, corrente de partida e comportamento da L298N.

A referência oficial de alimentação da Pi 5 está registrada no [[vault-slamderson/05-fontes/Catalogo-de-fontes|catálogo de fontes]].

Quantidade e formato das pilhas estão definidos; a adequação elétrica do conjunto permanece pendente. Uma fonte limitada em bancada não substitui automaticamente a proteção necessária quando se passa a usar uma bateria de alta corrente. Um corte de alimentação acessível e ensaio inicial com rodas suspensas são suficientes como organização básica do protótipo, sem impor arquitetura industrial.

## Sources

[1] https://einstronic.com/product/infrared-speed-sensor-module — Einstronic — MH Infrared Speed Sensor Module
[2] https://cdn.velleman.eu/downloads/25/wpse347a4v01.pdf — Velleman — WPSE347: IR speed sensor module
[5] https://www.ti.com/lit/ds/symlink/lm393.pdf — Texas Instruments — LM393: Dual Comparators
[23] https://pip.raspberrypi.com/documents/RP-009856-WP — Raspberry Pi Ltd — USB Power Delivery on Raspberry Pi 5
