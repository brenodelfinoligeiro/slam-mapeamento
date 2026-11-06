# R02 — Basike real e carcaça removível

**Revisão anterior preservada. A montagem atual é a [R03 com suporte C1 compacto](../carcaca-r03/LEIA-ME.md).** Os arquivos desta pasta e seu ZIP continuam sendo R02, sem atualização silenciosa das tampas/suporte.

Revisão solicitada pelo autor: corrigir o powerbank real e cobrir a eletrônica. Esta pasta supersede o [estudo 3D aberto R01](../montagem-3d/LEIA-ME.md), que foi preservado. É um **estudo geométrico de protótipo**, não uma montagem física validada ou um projeto liberado para fabricação.

## Arquivos

- [Prancha com quatro vistas](prancha-r02.png).
- Fechado: [frente](fechado.png) e [traseira](traseira.png).
- [Interior em níveis separados](interior.png) e [acesso às tampas](acesso.png): apresentações explicativas, não poses de operação.
- [Montagem completa FreeCAD](slamderson-coberto-r02.FCStd).
- [Somente a carcaça no FreeCAD](carcaca-estudo-r02.FCStd) e [STEP das peças de carcaça](carcaca-estudo-r02.step).
- [Pacote de estudo da carcaça](carcaca-estudo-r02.zip): seis STL, CAD da carcaça, STEP, gerador e documentação. Não inclui os CADs originais dos componentes nem significa aprovação para imprimir e montar sem conferir medidas.
- [Parâmetros/procedência](parametros-r02.json), [verificações geométricas](validacao-r02.json) e [recibo do render](render-r02.json).

## Distribuição corrigida

O [Basike informado pelo autor](../vault-slamderson/01-componentes/Powerbank-Basike.md) agora usa envelope **150 × 70 × 30 mm**, sem ser redimensionado ao volume antigo. A indicação de massa de **420 g** está registrada como leitura de balança, não pesagem certificada. Cantos, detalhes de carcaça e posições das portas/cabos continuam simplificados.

- Powerbank no **berço traseiro baixo**, com base em z=50,8 mm e topo em z=80,8 mm. Berço e cintas foram refeitos; a retirada é para trás, pela portinhola.
- Quatro AA na parte baixa dianteira, acessíveis pela portinhola frontal. Holder e discos seguem ilustrativos; as fendas do modelo não especificam resolução de encoder.
- ESP no segundo piso, como reserva de placa ainda não escolhida. A MPU continua rigidamente na base, próxima ao centro. L298N 4 mm à frente da posição R01, para deixar espaço ao powerbank.
- Colunas traseiras deslocadas para braços laterais fora do volume do Basike. Piso superior em z=87–90 mm, com nervuras e recortes para não atravessar as orelhas da carcaça.
- Pi no segundo piso. O C1 e sua ponte sobem 5 mm em relação à R01; a base do corpo C1 fica em z=145 mm.

A posição baixa reduz a altura do volume pesado, mas **não comprova estabilidade ou centro de massa**. Não há massa medida de todos os componentes, cálculo estrutural ou ensaio dinâmico.

## Carcaça proposta — seis peças

1. **Saia inferior ventilada**, com arcos livres para as rodas e apoios propostos ao piso.
2. **Tampa superior esquerda**.
3. **Tampa superior direita**.
4. **Portinhola frontal das AA**.
5. **Portinhola traseira do powerbank**.
6. **Painel lateral de serviço do powerbank**.

Corpo principal com envelope proposto de **170 × 212 mm**, paredes de **3 mm** e junta de estudo de **0,6 mm** entre metades. Dimensões não incluem todos os fixadores ilustrativos. Os maiores STL devem ser orientados e conferidos no fatiador; não foi realizado fatiamento nem ensaio de impressão.

As duas metades superiores saem lateralmente por rasgos ao redor dos apoios do C1; não é necessário puxar uma tampa verticalmente através da ponte. Os fixadores são representações e furos propostos: tipo de parafuso, inserts, tolerâncias e compatibilidade com a chapa real permanecem pendentes.

A eletrônica fica coberta nas vistas fechadas. Grandes janelas abertas foram substituídas por painéis removíveis e pequenas passagens de cabo. Não foram inventados recortes precisos USB/Ethernet a partir de posições não medidas. Conectar/acessar algumas interfaces exige abrir o painel ou a tampa; conferir cabos e raio de curvatura no hardware antes de fechar.

O teto tem grelhas sobre a região da Pi, há respiros laterais e passagem proposta de cabo do C1. A cobertura termina em z=137 mm, abaixo da base do corpo C1: **8 mm de diferença vertical nominal**. O corpo óptico fica exposto; não foi colocado plástico ou acrílico à frente da varredura.

**Não é uma caixa selada, estanque ou com grau IP.** Ventilação modelada não comprova refrigeração; cooler final, temperaturas e corrente real precisam de ensaio com o robô coberto.

## Validação executada

- Montagem salva e reaberta no kernel FreeCAD: **110 objetos**.
- Seis peças principais: um sólido BREP válido por peça. Seus seis STL foram reimportados como malhas fechadas; isso não certifica tolerância ou imprimibilidade.
- **60 testes conservadores de interseção** entre peças da carcaça e envelopes de componentes/berço/cintas; sem volume de interseção nas verificações feitas.
- Contato carcaça/piso conferido usando a geometria efetiva. Foram corrigidas interferências das nervuras com as orelhas do piso.
- Volume reservado para as rodas conferido com raio conservador; folga radial de estudo de aproximadamente 5 mm.
- Retirada lateral das tampas conferida contra os apoios do C1 em cinco posições, e retirada das AA/PB contra as peças da carcaça em cinco posições cada, com a portinhola correspondente removida. **São amostras discretas, não prova contínua de todo o movimento**; não incluem cabos, cintas flexíveis, deformação ou dedos/ferramentas.
- Renders no Blender 5.2.3 LTS/Cycles derivados do FCStd reaberto: 105 malhas, 1.401.671 triângulos. As quatro vistas e a prancha foram inspecionadas visualmente, inclusive o fechamento das placas.
- O arquivo R01 e os originais dos componentes foram preservados e conferidos por hash. A revisão é entregue separadamente, sem substituir arquivos antigos ou fazer push.

## Reprodução

```bash
/usr/bin/python docs/carcaca-r02/gerar-r02.py
/usr/bin/python docs/carcaca-r02/validar-r02.py
/usr/bin/python docs/carcaca-r02/exportar-cena.py
```

`renderizar-blender.py` recebe a pasta da cena como argumento após `--` e só modifica objetos de render. Não executar macros de arquivos de terceiros. Após regenerar derivados, atualizar seus hashes no [inventário local](../arquivos-somente-locais.json), preservando os hashes dos originais.

## Antes de fabricar

Conferir medidas e furação da chapa, holder, ESP, cantos/portas/cabos do Basike, alinhamento dos encoders, acesso aos conectores, fixação de 420 g, folgas físicas, material, orientação/suportes de impressão e temperatura em carga. Os STL são **para avaliação dimensional**, não peças aprovadas para montagem final. A carcaça não corrige as limitações elétricas das quatro AA/L298N nem transforma a saída USB-C 5 V/3 A do Basike em 5 A.
