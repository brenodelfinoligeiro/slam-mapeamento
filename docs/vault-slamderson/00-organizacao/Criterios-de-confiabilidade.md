---
tipo: metodologia
atualizado: 2026-11-04
---
# Critérios de confiabilidade

## Hierarquia adotada

1. Datasheet ou manual publicado pelo responsável pelo componente exato, com revisão identificada.
2. Documento desse autor hospedado por um distribuidor: preservar autoria e declarar a hospedagem intermediária; não afirmar equivalência binária com um original não acessado.
3. Manual de fabricante de **outro módulo semelhante**: usar como comparação e exemplo de funcionamento, não como especificação do hardware instalado.
4. Página comercial: serve para caracterizar a oferta e identificar uma associação de nomes, não para garantir revisão, circuito e limites de uma placa sem rastreabilidade.
5. Fórum, tutorial e anúncio sem procedência: pistas de investigação, não especificações finais.

Essa hierarquia é um critério metodológico do projeto, não uma garantia de ausência de erros. Verificar coerência dimensional, condições de teste e aplicabilidade. Uma marca confiável não corrige uma equação incorreta.

## O que acompanha cada afirmação

- Qual objeto: circuito integrado, módulo comercial, conjunto disco/sensor ou robô completo.
- De onde veio: referência, página/seção, revisão e data de acesso.
- Natureza: informado pelo autor, documentado, inferido ou medido.
- Limite: o que a fonte não permite concluir.

Datasheet de comparador não define alimentação de toda uma placa com emissor óptico, LEDs e resistores. Manual de outro módulo não define a ordem física dos pinos do módulo instalado.

## Situação da pesquisa

Não foi localizado um datasheet primário que identifique inequivocamente o fabricante e a revisão exata dos módulos `mh-sensor-series` do carrinho. A pesquisa encontrou uma associação comercial com FC-03/LM393 e documentação técnica de comparação, discutida em [[01-componentes/Encoder-MH-Sensor-Series]].

A integridade local é conferida por hash e leitura do PDF; isso detecta alteração dos bytes guardados, não certifica a autenticidade criptográfica da publicação. Resultados de busca e snippets não substituem a leitura do documento.
