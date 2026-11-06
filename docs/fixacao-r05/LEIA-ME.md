# R05 — insertos e retenção rígida (protótipo dimensional)

**CAD/STL gerados e auditados, não liberados para fabricação final.** Não houve impressão, montagem física, ensaio térmico, ensaio de carga dos 420 g ou operação do robô. A geometria real de chassi, holder, ESP e fixação do C1 continua pendente.

## Entregas prontas para ensaio dimensional

- [ZIP somente STL](slamderson-STL-Ender3V3SE-r05.zip): 28 modelos/44 impressos em `pecas/` e um cupom P25 em `00-cupom/`, 29 arquivos no total. Nomes indicam as quantidades. Não contém G-code.
- [Manual R05 de montagem e seis vistas](slamderson-r05-montagem-e-seis-vistas.pdf): 41 páginas, sendo 12 de guia e 29 fichas, uma por modelo/cupom, 174 projeções. Não usar instruções R04.
- `auditoria-orca.json` e `auditoria-slicer-hashes.json`: 29/29 modelos fatiados pelo OrcaSlicer 2.4.2 com perfil Ender-3 V3 SE, sem avisos no `result.json`. Material de referência Generic PLA, bico0,4/camada0,2; não é calibração física. G-code de auditoria fora da entrega.
- `validacao-pdf-r05.json`: texto/glyphs, seis imagens por ficha e 41 páginas rasterizadas; contatos e páginas selecionadas inspecionados visualmente.

**Primeiro o cupom.** Pilotos em orientações diferentes exigem ensaio correspondente; um cupom em Z não aprova automaticamente furos horizontais. Antes do lote, conferir também as interfaces físicas que continuam pendentes.

## Arquivos desta entrega

- `slamderson-fixacao-r05.FCStd`: montagem completa; peças próprias com `CodigoPeca` e `CorDoEstudo`, referências e ferragens separadas. Reaberto pelos validadores.
- `pecas-impressao-r05.FCStd`: catálogo das orientações individuais, **não é uma mesa única**.
- `cupom-insertos-r05.FCStd`: cupom independente P25.
- `stl/`: 29 modelos em mm, 28 tipos/44 peças da montagem e um cupom separado. **P21 foi eliminado**: apoios Pi integrados ao piso.
- `kit-r05.json`: quantidades, objetos de cada instância, orientação de impressão, SHA de cada STL, ferragens e 68 insertos com coordenadas/direções reais no referencial CAD.
- `lista-pecas.csv`, `validacao-*.json`, scripts e logs: evidência reproduzível. ZIP/PDF e auditoria Orca foram concluídos na integração final, sem alterar os STL.

## Parâmetros de insertos e parafusos

Medidas informadas pelo autor: M3, comprimento **5,68 mm**, Ø4,0 liso/Ø4,7 dentado. O valor antigo 10,7 mm foi superado. `requisitos-insertos.json` é mantido pelo agente principal, não por este gerador.

Piloto Ø4,3 e profundidade 6 mm são **propostas**, não recomendação identificada de fabricante nem ensaio aprovado. O cupom tem pilotos Ø4,2/4,3/4,4, todos com profundidade 6 mm e fundo 2 mm. Visto por cima, com o canto chanfrado à frente/esquerda: X11 = 4,2; X33 = 4,3; X55 = 4,4, todos em Y14. Instalar termicamente os insertos antes de experimentar resistência/extração/torque e ajustar o projeto se necessário. Não aplicar força para inserir a frio.

Os 68 alojamentos passaram pela verificação BREP de **2 mm radiais ao redor do envelope Ø4,7** e **2 mm de fundo**. A interpenetração de 0,2 mm radial entre inserto Ø4,7 e piloto Ø4,3 é intencional para instalação térmica, não uma colisão acidental. Rosca apenas nominal, sem hélice; conferir a ferragem física.

| Ferragem | Quantidade |
|---|---:|
| M3×8 Allen cilíndrico | 58 |
| M3×8 escareado 90° | 4 |
| M3×10 escareado 90° | 4 |
| M3×12 Allen cilíndrico | 2 |
| Inserto M3 5,68 × Ø4,0/4,7 | 68 |
| Arruela M3, espessura assumida 0,5 mm | 60 |
| Porcas, velcro, faixas ou cintas plásticas | **0** |

Engate calculado dos parafusos: 4,1–5,2 mm, inferior a 5,68 mm. Folga mínima da ponta ao fim do inserto 0,48 mm e ao fundo do piloto 0,8 mm. As cabeças/arruelas não invadem peças próprias nem placas/envelopes no CAD auditado. Não há parafuso passante M3×50/60 nem bolsos sextavados nas peças próprias R05.

## Mudanças de interface

- **Pi**: furos Ø2,7 do CAD de referência preservados; quatro pinos poliméricos Ø2,2 × 0,8 localizam, não há metal atravessando o PCB. P27: quatro presilhas externas por M3 nos bosses do piso. Apoios Z96; PCBtop97,276; presilha underside97,8. Eventual pad isolante precisa ser medido, sem apertar componentes/trilhas.
- **MPU**: P23 é um berço único no chassi, não na gaveta de bateria. Duas P28 seguram bordas e dois pinos Ø2,2 localizam. Deslocamento real desta revisão em relação à R04: **−12 X, −3 Y, +8 Z**. A mudança de extrínseca IMU deve ser medida/calibrada e refletida posteriormente no ROS; nenhum software foi alterado.
- **L298N**: o ensaio encontrou terminais do CAD colidindo com cabeça/arruela M3 sobre dois furos. Não modificar PCB: P22 virou berço único com quatro pinos Ø2,2 nos furos e bosses externos; P30 é quadro rígido de borda, preso por dois M3. Deslocamento R04→R05: **−3 Y, +4 Z**. Centros dos apoios (6/43,87/124), PCBbottom62,4. Não reutilizar as ferragens superiores M3×6 propostas antes da auditoria. Travessas P17 ganharam alívio simétrico para continuarem congruentes e liberarem o boss externo. Conferir resistência física das travessas/berço e folgas reais de rodas/cubos; o CAD de referência não é medição do robô.
- **ESP**: P24/P26 rígidos, sem furos fictícios nem passagens para velcro. Quadro sobrepõe 1 mm da projeção periférica do envelope; underside110,4 deixa 1,4 mm acima do envelope109. Isso comprova captura do **envelope**, não bordas livres da placa real. Medir PCB e componentes; redesenhar dedos antes de fabricar se as bordas não estiverem livres. Não apertar sobre componentes.
- **Holder**: P14 e duas réguas removíveis P29 permitem introdução por cima, sem flexionar ou aprisionar o holder durante a fabricação. Bosses X±44/Y6 e74. Réguas fora das células ilustrativas; batente plano P07 a Y9,6 fica 0,4 mm à frente do holder. Holder comercial não imprimir. A captura é condicional à medição do holder real.
- **Powerbank**: P13 é gaveta/sleeve rígido, com apoio plano, laterais de 1 mm de folga, lábios superiores com 0,6 mm de folga e alívios nas orelhas da saia. Envelope deslocado +1 Y para 136..206; batente plano P08 em Y206,4. Dois escareados horizontais fixam P13 às colunas traseiras. Janela USB Y145..195/Z58..76 é apenas provisória; não comprova acesso às portas reais. Sem pressão pontual sobre a bateria e sem prova estática.
- **C1**: colunas OD10 em X±25,5/Y84 com insertos opostos e parafusos separados para piso e base. Escareados superiores não invadem o corpo C1. Base 62×62 e corpo a Z145 preservados. Matriz ilustrativa 43×43 e quatro P20 **não definem fixação real**. Nenhum parafuso foi inventado no sensor. Medir rosca, matriz e profundidade antes de montar.
- **Portinholas AA/PB**: entradas dos insertos foram levadas às faces externas Y−2/Y210 para permitir a passagem do inserto e do ferro; não tentar inserir Ø4,7 por um furo passante Ø3,4. Por isso E/F usam M3×8 (engate5,1), não M3×10.

## Sequência e acessos obrigatórios

1. Ensaiar P25 e definir material/parâmetros de instalação. Nenhuma temperatura foi presumida.
2. Instalar **todos os insertos em peças separadas**, sem PCBs, bateria, chassi ou peça conjugada. O ensaio BREP usou ponta hipotética OD7 por15 mm e haste OD10 por20 mm, livres contra a própria peça em cada uma das 68 entradas. Não substitui conferir seu ferro real. Linguetas: instalar antes de juntar frente/trás; P11: antes de colocá-los nas paredes; piso/P24/P14/colunas: instalar ambos os lados antes de fechar o conjunto.
3. Conferir chassi físico: espessura3 mm e posições de furos são referência CAD, não autorizam furar sem gabarito. Montar P14/P22/P23 e colunas P15/P16/P17 com parafusos de baixo, sem a bateria. Introduzir holder por cima e prender P29; montar MPU/L298 com presilhas/quadro. Presilhas apoiam em batentes duros: torque não deve comprimir PCB.
4. Prender P13 às flanges P16 por dois escareados horizontais (grupo L) **antes de introduzir PB**. Cabeças embutidas, sem avançar sobre PBfront136.
5. Montar saia e P11 inferiores. Preparar módulo superior na bancada: apoio/localização Pi e presilhas; P24 pelo lado de baixo do piso, ESP e P26; colunas C1 fixadas pelo lado de baixo do piso. Montar piso nas colunas principais com I2 e na saia com **H escareado de baixo**, antes de colocar o powerbank, pois os acessos H traseiros ficam acima dele. Não antecipar a entrada do PB.
6. Unir pares de teto pela lateral e por P10, colocar no conjunto e prender somente os quatro A superiores para retenção removível. P19 estrutural nas colunas P18 por J2 escareado; **sensor não montar** sem medir sua interface. Nenhuma necessidade de M3 atravessar o sensor.
7. Introduzir PB deslizando de trás para frente, com P08 removida; fechar P08 e P09. Não apertar batentes contra o corpo da bateria.

### Retirada auditada

- Teto: retirar **quatro A superiores**, mantendo C/D para cada par de quartos e ponte P10 se moverem juntos. **Elevar 2 mm e depois deslocar a metade lateralmente**, até110 mm amostrados. Movimento apenas horizontal colide com bosses F; não usar o roteiro R04 de puxar diretamente de lado. Ao elevar, teto vai a139 mm, abaixo da baseC1 em140 mm. Teste contra todas as peças fixas e placas/envelopes; é amostragem, não prova de trajetória contínua.
- PB: P08 retirada, deslizar para +Y; posições 0/1/5/20/40/75/100 mm foram testadas sem interseções. P13 fica instalado.
- Células AA: manutenção vertical foi ensaiada com o **módulo superior/teto desmontado**; não apresentar troca de pilhas por cima com o piso presente. As réguas P29 não interceptam as quatro células ilustrativas. Geometria comercial real permanece pendente.

## Evidência e reprodução

`validacao-montagem-r05.json`: 44 sólidos únicos válidos; 946 pares próprios, 308 pares contra placas/envelopes, 5.632 ferragem×plástico, 896 ferragem×componentes, 68 alojamentos, 476 inserto×componentes; 2.430 verificações de retirada de teto, 343 de PB e480 de células, **zero erros**. SHA das três fontes R04 preservados.

`validacao-funcional-r05.json`: 68 acessos térmicos livres em peças isoladas, quatro capturas verticais e16 instâncias repetidas congruentes por rotação rígida. Captura vertical: Pi livre0,50/bloqueada0,60 mm; MPU/L298 livre0,45/bloqueada0,60; ESP livre1,35/bloqueada1,50. Não é ensaio de carga ou validação de pads.

`validacao-referencias-r05.json`: 1.584 pares contra cilindros circunscritos de rodas/cubos e caixas conservadoras dos demais meshes de referência, zero interseções próprias. Não verifica furos dos parafusos no chassi físico.

`validacao-stl.json`: todos29 STL reabertos com Trimesh, fechados, orientação consistente, uma componente, volume positivo, Z mínimo0, dimensões/volume conferidos contra CAD/mm e SHA. Maior XY202,499 mm aproximadamente; sobra mínima após brim5 é3,750 mm por lado, maior que margem3 exigida. Ender3 V3 SE220×220×250; bico0,4/camada0,2 são hipóteses. Fatiamento complementar concluído na integração final: todos29 modelos, sem avisos, hashes conferidos contra os bytes entregues.

`validacao-entrega-r05.json`: consolidação com SHA dos artefatos, caixas CAD de todas44 instâncias, reabertura dos três documentos FreeCAD e19.110 pares ferragem×ferragem sem interseção volumétrica. Margens mínimas de ponta confirmadas:0,48 mm até fim do inserto e0,8 mm até fundo do piloto.

```bash
cd /home/lamggm/projects/slamderson_ws/docs/fixacao-r05
/usr/bin/python gerar-r05.py
/usr/bin/python validar-montagem.py
/usr/bin/python validar-funcional.py
/usr/bin/python validar-referencias.py
uv run --no-project --with trimesh --with numpy --with networkx python validar-stl.py
/usr/bin/python consolidar-entrega.py
```

FreeCAD é carregado antes de Part via `/usr/lib/freecad/lib`. Nenhuma instalação global, commit/push, operação de hardware ou arquivo R04 foi alterado. Os renders/PDF R05 foram gerados depois dos validadores, sem modificar CAD/STL; notas e índices foram sincronizados. Derivados com proveniência/licença pendente continuam locais.
