# R03 — suporte compacto do C1

O autor rejeitou a largura/aparência da ponte da R02. Esta revisão reduz o suporte sem redimensionar o sensor ou mover a eletrônica. A [R02](../carcaca-r02/LEIA-ME.md) e seus CADs/renders são preservados como anteriores; a R03 é a montagem atual proposta.

## Alterações

- Base antiga: **130 × 66 × 3 mm**. Nova base: **62 × 62 × 3 mm**, com cantos arredondados de raio proposto de 8 mm. Redução de largura de aproximadamente **52,3%**.
- Dois apoios saem de x=±58/y=80 mm para **x=±21,5/y=82,5 mm**, dentro da projeção do corpo do C1 e apoiados na região sólida do piso. Os apoios não ficam pousados no vazio da janela do L298N.
- Base, apoios e espaçadores passam de rosa para carvão, integrando visualmente o suporte ao sensor.
- Rasgo de 126 mm das tampas eliminado; novo rasgo de **54 × 11 mm**, sob a base compacta, com passagem de cabo proposta separada. As tampas continuam com retirada lateral.
- Sensor mantido em **z=145 mm na base do corpo**, teto em **z=137 mm**. A revisão não adiciona paredes junto à região superior de varredura nem afirma ensaio óptico.
- A matriz de furos dos espaçadores da R02 foi preservada como proposta, agora com furos de passagem no suporte. **Não é furação confirmada do C1 físico.** Medir antes de fabricar.

Basike real de 150 × 70 × 30 mm, berço baixo, quatro AA, Pi, ESP, L298N e IMU permanecem nas posições da R02. A carcaça continua ventilada, sem vedação/grau IP. Nenhum arquivo original de componente foi modificado e não houve push.

## Arquivos

- [Comparação antes/depois](comparacao-r02-r03.png), com o mesmo enquadramento e iluminação.
- Renders: [frente](fechado.png), [traseira](traseira.png), [detalhe do C1](detalhe.png) e [acesso às tampas](acesso.png).
- [Montagem completa FreeCAD](slamderson-coberto-r03.FCStd).
- [Somente o suporte editável](suporte-c1-estudo-r03.FCStd) e [STEP do suporte](suporte-c1-estudo-r03.step): base, dois apoios e quatro espaçadores. São geometrias de estudo, não peças liberadas para montagem final.
- [Parâmetros e hash de origem](parametros-r03.json), [validação](validacao-r03.json) e [recibo do render](render-r03.json).

Os STL/tampas da R02 continuam sendo a revisão anterior, não arquivos sincronizados silenciosamente com esta revisão.

## Verificações executadas

- FCStd completo reaberto: 110 objetos; BREP das peças válidos. Dimensões da base e centros dos apoios conferidos no arquivo reaberto.
- Contato dos pés com o piso conferido geometricamente; suporte sem interseção volumétrica com tampas, Pi, ESP e corpo C1. Faces de contato entre peças são permitidas.
- Retirada lateral das duas tampas conferida contra base, apoios e espaçadores em seis posições: 0, 5, 15, 40, 80 e 110 mm. Amostras discretas, não prova contínua do caminho ou ensaio de montagem.
- Reexecutadas 60 verificações conservadoras da carcaça contra envelopes dos componentes/berço/cintas, folgas modeladas das rodas e amostras de retirada das AA/PB com a portinhola correspondente removida.
- Testes usam descarte por caixas sem interseção interior antes de operações booleanas: contato de faces sem sobreposição de volume não é colisão. Quando há sobreposição de caixas, a geometria efetiva é comparada.
- Renders derivados do FCStd reaberto, sem mover peças no render fechado. A vista de acesso afasta tampas/portinholas apenas para apresentação. Inspeção visual confirma retirada da prateleira larga; isso não comprova dimensões físicas.

## Reprodução e limites

```bash
/usr/bin/python docs/carcaca-r03/gerar-r03.py
/usr/bin/python docs/carcaca-r03/validar-r03.py
/usr/bin/python docs/carcaca-r03/exportar-cena.py
```

Gerador depende da R02 local preservada. Renderer recebe a pasta da cena após `--`; utilizar Blender com autoexecução de terceiros desativada. Os originais do CAD continuam sob seus avisos de procedência e limitações de redistribuição.

**Antes de fabricar:** medir furação do sensor e da chapa, conferir parafusos/inserts, acesso real ao cabo, material/orientação de impressão, rigidez da base em balanço, vibração e temperatura com a tampa fechada. O suporte compacto ainda não foi submetido a ensaio estrutural ou de hardware.
