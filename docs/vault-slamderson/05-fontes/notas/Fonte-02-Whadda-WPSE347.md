---
tipo: fonte
referencia_id: 2
classe: manual_de_modulo_semelhante
aplicabilidade: comparacao_com_ressalvas
consulta: 2026-11-04
---
# Fonte 02 — Whadda/Velleman WPSE347

Manual “IR speed sensor module”, identificado como WPSE347_v01, com sete páginas, obtido do CDN da Velleman. Descreve um módulo óptico baseado em LM393, com D0 e A0. Não foi comprovado que o módulo do carrinho corresponda a esse produto.[2]

## Contradição elétrica

Na página 3, o manual afirma “VCC: module power supply from 3.0 to 12 V.”. Na página 4, especifica “working voltage: 3.3-5 VDC”. O documento também descreve pulsos de 0 a 5 V, sem esclarecer nessa passagem a dependência da alimentação e do circuito.[2]

Não selecionar a maior faixa como se a divergência fosse uma autorização. Para o MH instalado, a alimentação e a saída continuam pendentes de identificação e verificação; **não aplicar 12 V com base nesse manual**.

## Erro de cálculo na página 3

O exemplo publicado associa uma fenda e intervalo de três segundos a 180 RPM; para duas fendas, informa 90 RPM.[2]

A derivação independente por conversão de unidades é RPM = 60/(C T), para eventos igualmente espaçados e C eventos contados por volta. Para os valores do exemplo, a execução em Python retornou 20 e 10 RPM, respectivamente. São cálculos idealizados, não medições dos encoders do carrinho.

O manual multiplica pelo intervalo quando deveria dividi-lo. Não usar sua fórmula ou seus exemplos como referência correta para cálculo de rotação. Veja [[02-fundamentos/Contagem-e-odometria]].

## Uso permitido nesta pesquisa

Serve como documentação de funcionamento de **outro módulo**, indicação de nomes de sinais e exemplo de por que uma fonte primária também precisa de análise crítica. Não resolve a alimentação, a ordem física dos pinos ou a revisão do MH-Sensor-Series.

## Original e evidências

[[05-fontes/pdf/velleman-wpse347.pdf|PDF original]] · [[05-fontes/evidencias/velleman-wpse347.txt|Texto extraído]]

[[01-componentes/Encoder-MH-Sensor-Series]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[2] https://cdn.velleman.eu/downloads/25/wpse347a4v01.pdf — Velleman — WPSE347: IR speed sensor module
