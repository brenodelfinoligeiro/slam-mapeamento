---
tipo: componente
identificacao_autor: mh-sensor-series
estado: identificacao_parcial
atualizado: 2026-11-04
---
# Encoder MH-Sensor-Series

## Evidência do projeto

O autor identifica os módulos como `mh-sensor-series`; as fotografias anteriores mostram a inscrição `MH-Sensor-Series`, sensor óptico em garfo e disco fendido acoplado ao motorredutor. Aparentemente há um canal por roda. Não foram confirmados código do circuito integrado, pinagem, alimentação ou contagens por volta.

Após examinar a prévia CAD, o autor confirmou que o sensor óptico extraído da montagem corresponde visualmente ao encoder do projeto. Essa confirmação permite adotá-lo como referência mecânica identificada pelo autor; medidas, furação e características elétricas continuam a verificar. Veja [[01-componentes/Modelos-3D]].

## O que a pesquisa acrescenta

A Einstronic vende um “MH Infrared Speed Sensor Module”, associa a família a FC-03 e LM393 e anuncia alimentação de 3,3–5 V e saídas digital/analógica. Isso documenta **o produto anunciado**, não a identidade elétrica da placa instalada.[1]

A Whadda/Velleman publica um manual do WPSE347, módulo óptico de velocidade com LM393 e saídas D0/A0. É uma referência de um módulo semelhante, não prova de que o MH-Sensor-Series seja o WPSE347.[2]

A Texas Instruments descreve o LM393 como comparador com saída de coletor aberto. Se o circuito integrado da placa for confirmado como LM393, esse datasheet ajuda a compreender a saída; a tensão em D0 ainda depende das ligações, resistores e indicadores da placa.[5]

## Consequência para a integração

- Não assumir que todos os módulos com a inscrição usam o mesmo circuito.
- Não copiar a posição dos pinos de uma foto comercial. Conferir inscrições e continuidade no módulo real, desenergizado.
- Antes de conectar D0 ao ESP, verificar nível alto/baixo e referência comum com o sensor alimentado de maneira compatível com sua revisão.
- Não assumir que alimentar um módulo a 5 V produz automaticamente uma saída segura de 3,3 V. Havendo incompatibilidade, definir condicionamento adequado após examinar o circuito.
- Alimentação, limiar de leitura, contagem de bordas e resolução são parâmetros a validar, não dados já medidos.

## Limitações das referências

O manual WPSE347 contém contradições sobre alimentação e um exemplo incorreto de RPM. Não utilizar a menção a 12 V para alimentar os módulos do carrinho. A análise está em [[05-fontes/notas/Fonte-02-Whadda-WPSE347]].[2]

A afirmação comercial sobre FC-03/LM393 fortalece uma hipótese, mas não substitui leitura da marcação e caracterização do módulo real. Não foi encontrado um PDF primário que resolva essa identificação exata.

## Documentos e próximo passo técnico

- [[05-fontes/notas/Fonte-01-Einstronic-MH|Página comercial arquivada e limites]].
- [[05-fontes/notas/Fonte-02-Whadda-WPSE347|Manual comparativo e análise crítica]].
- [[05-fontes/notas/Fonte-05-TI-LM393|Datasheet do comparador, aplicabilidade condicional]].
- [[04-experimentos/Caracterizacao-dos-encoders|Procedimento proposto de caracterização]].
- [[02-fundamentos/Contagem-e-odometria|Relação entre pulsos, velocidade e odometria]].

## Sources

[1] https://einstronic.com/product/infrared-speed-sensor-module — Einstronic — MH Infrared Speed Sensor Module
[2] https://cdn.velleman.eu/downloads/25/wpse347a4v01.pdf — Velleman — WPSE347: IR speed sensor module
[5] https://www.ti.com/lit/ds/symlink/lm393.pdf — Texas Instruments — LM393: Dual Comparators
