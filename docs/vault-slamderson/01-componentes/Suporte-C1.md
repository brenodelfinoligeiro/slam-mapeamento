---
tipo: componente
estado: proposta_geometrica
---
# Suporte compacto do C1

**Pedido do autor:** o suporte do LiDAR não precisa ser tão largo; a ponte da R02 ficou visualmente inadequada. Reduzir largura é requisito. As dimensões abaixo são a solução proposta, não medidas aprovadas do hardware.

Na [R03](../../carcaca-r03/LEIA-ME.md), a placa de 130 × 66 × 3 mm foi substituída por base de **62 × 62 × 3 mm**, com cantos arredondados. Os dois apoios foram aproximados para x=±21,5 mm, y=82,5 mm, sob a projeção do corpo do sensor e com contato geométrico no piso. Base/apoios/espaçadores usam carvão no estudo visual para eliminar a prateleira rosa.

A posição do corpo C1 não mudou: base em z=145 mm, acima do teto de z=137 mm. Rasgo das tampas reduzido para 54 × 11 mm sob a nova base; passagem de cabo é proposta. Retirada lateral das tampas passou nas seis posições amostradas contra base, apoios e espaçadores. Isso não prova varredura óptica real ou movimento contínuo sem cabos.

A matriz de furos é a proposta usada pelos espaçadores anteriores, **não uma especificação dimensional confirmada do C1 físico**. Antes de fabricar, medir furação e portas, definir fixadores, verificar acesso ao cabo, rigidez, vibração, material e orientação de impressão. Apoio menor não elimina a necessidade de ensaio estrutural.

## Fixação estrutural R05

A [R05](../../fixacao-r05/LEIA-ME.md) mantém base **62 × 62 × 3 mm** e corpo C1 em z145. Colunas P18 agora têm Ø10, centros x±25,5 / y84 e insertos opostos. J prende cada coluna ao piso por baixo; J2 escareado prende P19 ao topo. **Nenhum desses parafusos especifica a rosca do sensor.** P20 e a matriz 43 × 43 continuam ilustrativos, aguardando medição física.

Para retirar cada metade do teto: remover A superiores, elevar 2 mm e então deslocar lateralmente; movimento só horizontal colide com os bosses traseiros. Posições discretas passaram no CAD, sem prova de trajetória contínua com cabos reais.

[Comparação R02/R03](../../carcaca-r03/comparacao-r02-r03.png) · [Parâmetros](../../carcaca-r03/parametros-r03.json) · [Verificações executadas](../../carcaca-r03/validacao-r03.json).

[[03-decisoes/Arquitetura-atual]] · [[01-componentes/Modelos-3D]]
