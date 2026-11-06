---
tipo: componente
estado: exemplar_real_informado_pelo_autor
---
# Powerbank Basike

## Exemplar e evidência

O autor identificou este powerbank como o exemplar real para alimentar a Raspberry Pi. Marca **basike** visível na frente. O código de modelo parece `B-079B` na foto 1 do ZIP; essa leitura isolada deve ser confirmada antes de usar documentação de um SKU específico.

- Comprimento: **150 mm**; largura: **70 mm**, conforme anotações de 15 × 7 cm na foto enviada pelo autor.
- Espessura: **30 mm**, informada em texto pelo autor.
- Massa indicada na foto da balança: **0,420 kg / 420 g**. Não foram verificados tara, calibração ou incerteza; tratar como leitura indicada, não medição certificada.
- Invólucro preto, cantos arredondados, visor frontal e inscrição `22.5W SuperCharge`.
- Duas portas vistas na foto 3 do ZIP: USB-C e USB-A. Dois cabos integrados vistos nas fotos 1/2/5: USB-C e Lightning.

Originais e hashes: [registro de medição](../../medicoes/powerbank-basike/medicoes.json). O ZIP tem sete fotografias; todas foram extraídas para inspeção sem executar conteúdo, com CRC e hashes conferidos. As fotos de peso e medidas foram enviadas separadamente do ZIP.

## Dados elétricos legíveis

As fotos 1 e 2 do ZIP concordam nos seguintes dados impressos:

- Bateria interna declarada: **20000 mAh, 3,7 V / 74 Wh**.
- Capacidade nominal de saída declarada: **12000 mAh (5 V / 3 A)**. É declaração de etiqueta, não autonomia medida.
- Entrada USB-C: **5 V / 3 A; 9 V / 2 A; 12 V / 1,5 A**, máximo 18 W.
- Saída da porta USB-C e do cabo USB-C integrado: **5 V / 3 A; 9 V / 2,22 A; 12 V / 1,67 A**, máximo 20 W por saída conforme etiqueta.
- Cabo Lightning: **5 V / 2,4 A**, máximo 12 W.
- Saída total declarada: **5 V / 3 A, máximo 15 W**. Não somar os máximos individuais como se estivessem disponíveis ao mesmo tempo.
- USB-A anunciada como 22,5 W; a transcrição completa de seus perfis não foi consolidada porque as duas leituras das fotos divergem em um trecho. Não inferir que 4,5/5 A anunciados em USB-A estejam disponíveis à Pi pela USB-C.

Para a Raspberry Pi 5, o perfil observado é **5 V / 3 A**, não 5 V / 5 A. O conjunto pode ser avaliado no protótipo com carga/periféricos compatíveis, mas não equivale à fonte recomendada de 5 A. Verificar negociação real, cabo, subtensão, limite dos periféricos USB, aquecimento e comportamento durante a carga de ROS/LiDAR. Não forçar 9/12 V nos GPIOs ou na alimentação de 5 V da Pi. Não foi realizado ensaio elétrico.

## Retenção rígida R05

Na [R05](../../fixacao-r05/LEIA-ME.md), o autor eliminou porcas, velcro e cintas plásticas. P13 virou gaveta rígida: apoio plano, paredes com 1 mm de folga lateral e lábios com 0,6 mm de folga acima do envelope. O Basike foi deslocado +1 mm em Y em relação à R04, mantendo o envelope 150 × 70 × 30 e z50,8..80,8; agora ocupa y136..206. Dois escareados M3×8 prendem a gaveta às flanges das colunas traseiras. P08 tem batente plano em y206,4, sem comprimir a bateria.

O saque traseiro com P08 removida passou nas posições amostradas; o acesso H do piso precisa estar concluído antes de introduzir o Basike. A janela USB/botão continua provisória. Geometria e fatiamento não são ensaio da carga de 420 g, temperatura ou estabilidade.

## Consequências para o estudo mecânico (histórico)

O estudo 2D/R01 anterior usa uma reserva de **120 × 65 × 25 mm**, não este exemplar real. Foi preservado como histórico. A [R02 atualizada](../../carcaca-r02/LEIA-ME.md) já utiliza **150 × 70 × 30 mm**, em berço traseiro baixo com base em z=50,8 mm; o ESP foi transferido para o segundo piso. Cintas, piso e suportes foram revistos para liberar o volume do Basike, e foi modelada carcaça ventilada removível. Isso ainda não valida encaixe físico, resistência ou estabilidade.

Avaliação anterior, superada pela redistribuição da R02, caso o powerbank permanecesse transversal no piso superior antigo:

- Novo envelope: x de −75 a +75 mm; y de 135 a 205 mm; z de 91 a 121 mm.
- O piso tem 130 mm de largura: o powerbank de 150 mm fica com **10 mm de balanço por lado**.
- A ponte do C1 começa em z=135 mm: sob essa hipótese, há **14 mm entre o topo do powerbank e a face inferior da ponte**, sem contar cabos, cintas e tolerâncias.
- A cinta ilustrativa de 122 mm e o berço anterior não representam a retenção deste exemplar de 150 mm. Precisam ser redesenhados antes de qualquer fabricação.
- A leitura de 420 g torna necessária a avaliação de resistência dos apoios e estabilidade. Preferir posição baixa e próxima do eixo, se a redistribuição dos demais componentes permitir; isso ainda não é uma alteração de posição aprovada.

A conta de envelopes não verifica passagem de cabos, portas, botão, visor, fixação, balanço dinâmico ou centro de massa completo. Nenhuma peça foi aprovada para imprimir.

[[03-decisoes/Arquitetura-atual]] · [[06-ideias/Ideias-e-pendencias]] · [Estudo 3D anterior](../../montagem-3d/LEIA-ME.md)
