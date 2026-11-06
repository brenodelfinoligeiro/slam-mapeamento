# Disposição dos componentes — quatro AA

**Referência histórica de implantação:** a revisão 3D atual é a [R02 com Basike real e carcaça](../carcaca-r02/LEIA-ME.md). As vistas desta pasta não foram redesenhadas como se já incluíssem as mudanças posteriores.

Estudo preliminar solicitado pelo autor: **quatro pilhas AA** e powerbank separado para a Raspberry. A quantidade substitui o exemplo anterior de oito AA; não é aprovação elétrica da alimentação dos motores informados como 12 V.

## Arquivos

- [Prancha PNG](disposicao-componentes-2d.png): duas plantas, vista lateral e vista frontal.
- [SVG editável](disposicao-componentes-2d.svg): textos, cores e contornos vetoriais.
- [PDF](disposicao-componentes-2d.pdf): visualização vetorial; sem escala física de impressão definida.
- [FreeCAD 2D](disposicao-componentes-2d.FCStd): geometrias de contorno da prancha, com nomes dos componentes/camadas; **não** uma montagem 3D de sólidos nem TechDraw de fabricação.
- [Parâmetros e evidências](implantacao.json).
- Gerador reproduzível: `gerar-vistas.py`, executado com Python do sistema e módulos FreeCAD instalados.

## Proposta de montagem

Existe um [estudo 3D posterior](../montagem-3d/LEIA-ME.md): ele preserva a mecânica do CAD original e eleva ESP/L298N em 6 mm para liberar suportes dos motores. A prancha 2D desta pasta permanece como a proposta anterior; não foi redesenhada silenciosamente como se já incluísse esse ajuste.

- Piso inferior: holder das quatro AA na região arredondada; ESP e L298N em lados distintos; MPU-6050 fixada rigidamente ao piso. Motores, discos e garfos ficam sob a chapa, junto aos eixos.
- Piso superior removível: Raspberry à frente, powerbank preso com cinta atrás. Existe uma janela proposta sobre a L298N para não fechar completamente seu dissipador.
- Ponte elevada: corpo do C1 acima dos outros volumes, com os cabos mantidos abaixo da região óptica. A altura exata do plano de varredura não foi presumida.
- Impressão 3D proposta: quatro colunas principais, piso com janela, apoios e ponte do LiDAR. Não existem furação, espessuras ou tolerâncias aprovadas para impressão.

Frente convencional: extremidade arredondada, oposta ao rodízio. A frontal é vista dessa extremidade em direção ao rodízio, portanto as posições laterais aparecem espelhadas em relação à planta com a frente para cima. A origem vertical é o solo proposto, z=0.

## Dimensões e hipóteses

O [powerbank real informado posteriormente](../vault-slamderson/01-componentes/Powerbank-Basike.md) mede 150 × 70 × 30 mm e teve indicação de 420 g na balança. Esta prancha conserva a reserva anterior; não foi regenerada como se já representasse o exemplar real.

O contorno da chapa e suas aberturas vieram das bordas da superfície horizontal em z=48,418 do STL local do chassi B. O gerador preserva a procedência e não executa macros de terceiros. A interpretação em mm deriva da cena Blender já inspecionada; a chapa tem aproximadamente 149 × 210 mm no CAD, não medidos na peça real.

Os envelopes de Raspberry, L298N e MPU partem do manifesto CAD local. O C1 é representado pelo corpo simplificado, não pela caixa envolvente do STEP com acessórios. Motores, rodas, rodízio e encoders são representações funcionais simplificadas, não uma confirmação de alinhamento ou revisão física.

Holder (75 × 70 × 22 mm), ESP (28 × 55 × 15 mm), powerbank (120 × 65 × 25 mm), espaço de cooler, posições e níveis são **reservas/propostas**. O piso superior foi colocado em z=84–87 mm; ponte em z=135–138 mm; corpo C1 em z=140–181,3 mm. São parâmetros do estudo, não cotas de fabricação.

Quatro alcalinas AA em série correspondem a 6 V nominais; quatro NiMH, a 4,8 V. A L298N adiciona queda de tensão. O estudo mecânico **não comprova** partida, torque, autonomia ou alimentação adequada dos motores informados como 12 V. Não foi acrescentado elevador de tensão nem alterado o driver.

## Validação realizada e limites

A revisão final foi renderizada em PNG/PDF a partir do SVG e inspecionada visualmente; foram corrigidas notas sobrepostas e a orientação frontal. O arquivo nativo foi salvo e reaberto no kernel FreeCAD 1.1.4: 101 geometrias 2D não nulas/válidas e 102 objetos, incluindo a nota de escopo. Isso não equivale a inspeção GUI da bancada, ensaio físico, detecção completa de colisões 3D, análise estrutural ou cálculo do centro de massa.

Antes de fabricar: medir holder, powerbank e ESP; conferir contorno/furos do chassi; prever conectores, cabos e retirada das pilhas; alinhar encoders; dimensionar suportes e validar estabilidade, refrigeração e alimentação.

## Publicação

Os desenhos derivados do chassi permanecem locais, conforme [política de publicação](../publicacao-git.md), com hashes no [inventário](../arquivos-somente-locais.json). Nenhum commit ou push foi feito nesta tarefa. Os originais CAD foram preservados.

## Reprodução local

```bash
/usr/bin/python docs/disposicao-2d/gerar-vistas.py
rsvg-convert -o docs/disposicao-2d/disposicao-componentes-2d.png docs/disposicao-2d/disposicao-componentes-2d.svg
rsvg-convert -f pdf -o docs/disposicao-2d/disposicao-componentes-2d.pdf docs/disposicao-2d/disposicao-componentes-2d.svg
```

Após regenerar os desenhos, atualizar seus hashes no inventário de arquivos somente locais; não substituir hashes de originais de terceiros.
