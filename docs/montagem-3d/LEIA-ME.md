# Estudo 3D de montagem — quatro AA

**SUPERSEDIDO PELA [R02 COBERTA COM BASIKE REAL](../carcaca-r02/LEIA-ME.md).** Esta pasta é a R01 preservada: seus arquivos não foram sobrescritos. A descrição abaixo se refere ao estudo anterior.

O autor solicitou transformar a [disposição 2D](../disposicao-2d/LEIA-ME.md) em um estudo tridimensional. Mantêm-se quatro AA, Raspberry com powerbank separado, ESP, L298N, MPU-6050, encoders e C1. A montagem continua sendo **uma proposta**, não um conjunto aprovado para fabricação ou funcionamento elétrico.

## Entrega

**Atualização de evidência:** o autor posteriormente forneceu o [powerbank real Basike](../vault-slamderson/01-componentes/Powerbank-Basike.md), com 150 × 70 × 30 mm e leitura de massa de 420 g. Os arquivos de montagem e imagens abaixo ainda contêm a reserva anterior de 120 × 65 × 25 mm; não foram regenerados nesta coleta. A verificação de envelope e as consequências para retenção/estabilidade estão na nota do componente. Não tratar essas imagens anteriores como encaixe validado do exemplar real.

- [Prancha montada e explodida](prancha-3d.png).
- [Imagem montada](montagem-3d.png).
- [Imagem explodida](explodida-3d.png): grupos elevados somente para leitura, sem representar posições operacionais.
- [Arquivo FreeCAD editável](slamderson-estudo-3d.FCStd): árvore por grupos, malhas mecânicas de referência, sólidos importados e reservas/propostas.
- [Validação e procedência](validacao-3d.json), [validação de estilos](validacao-estilos.json) e [recibo do render](render-ok.json).
- Gerador: `gerar-montagem.py`. Requer os CADs locais, Python do sistema, NumPy e módulos FreeCAD instalados. O render usa tesselações do FCStd reaberto, sem descartar triângulos da mecânica.

## O que é real CAD, reserva e proposta

- Chassi, rodas, motores e rodízio: malhas do pacote Thingiverse 4738179 fornecido pelo autor, com suas posições relativas preservadas. Separadas em 36 componentes conexos, somando 684.152 facetas. O CAD é referência visual da família B; não comprova medidas ou revisão do carrinho real.
- Pi 5: STEP oficial completo, transladado sem redimensionamento.
- L298N, MPU-6050 e os dois garfos: CADs locais de referência. A identificação visual do garfo não confirma furação ou características elétricas.
- C1: corpo derivado do STEP local, preservando 15 sólidos localizados na região do corpo. Sete sólidos de cabo/acessórios externos foram omitidos; índices e hash de origem constam na validação. O corpo extraído mede aproximadamente 55,86 × 55,86 × 41,45 mm; não foi forçado ao círculo nominal da prancha 2D.
- Holder com quatro AA, ESP e powerbank: **reservas genéricas**, não modelos comerciais escolhidos. Células, polaridades aparentes e dimensões do holder são ilustrativas; o desenho não constitui esquema elétrico.
- Discos: geometria ilustrativa, com fendas desenhadas apenas para reconhecimento. **Não usar a contagem de fendas do modelo como resolução dos encoders reais.**
- Partes rosas: colunas, apoios, piso superior removível e ponte para o C1. São formas propostas para estudar montagem; não há autorização técnica para imprimir/usar os suportes ou assumir furação compatível.

## Ajustes encontrados ao passar do 2D ao 3D

ESP e L298N foram elevados **6 mm**, passando a ter o fundo dos respectivos envelopes em z=56,4 mm. Isso evita a sobreposição vertical evidente com suportes dos motores que chegam a cerca de z=54,1 mm no CAD de origem. A janela do piso superior fica sobre a L298N; isso não certifica refrigeração.

A mecânica usa as posições originais dos eixos/rodas/rodízio, não as posições aproximadas dos círculos do estudo 2D. A pose dos garfos/discos continua pendente de alinhamento nos motores reais. Nenhuma medição de centro de massa, folga do pneu, retenção de pilhas/powerbank, cabos, conectores, cooler ou estabilidade foi executada.

## Validação realmente realizada

O arquivo nativo foi criado e reaberto no kernel FreeCAD 1.1.4: 86 objetos, 5.728 sólidos BREP contabilizados, 36 malhas e nenhum objeto BREP inválido detectado. As malhas permanecem malhas; essa contagem não afirma que sejam sólidos fechados ou que não haja colisão entre componentes.

A renderização OpenGL na GUI local gerou imagens vazias e foi rejeitada. Não se apresenta esse resultado como validação visual. Os renders entregues foram produzidos no Blender 5.2.3 LTS/Cycles, a partir de 84 malhas exportadas do FCStd reaberto, somando 1.384.533 triângulos. Uma primeira exportação que aplicava a transformação da malha duas vezes foi corrigida; a exportação final usa `Mesh.Topology` já em coordenadas transformadas.

A aparência/câmera da GUI foi incorporada ao arquivo nativo sem alterar `Document.xml` ou os blobs geométricos; os hashes de 127 membros protegidos foram comparados. As imagens montada/explodida e a prancha final foram inspecionadas visualmente, sem cortes impeditivos. Isso não substitui uma análise completa de colisões ou ensaio físico.

## Alimentação e publicação

Quatro alcalinas AA em série correspondem a 6 V nominais, antes das perdas na L298N; quatro NiMH, a 4,8 V. Não foi acrescentado elevador de tensão nem validado o desempenho dos motores informados como 12 V.

Os originais foram preservados. Imagens e modelo derivados permanecem locais, conforme [política de publicação](../publicacao-git.md) e [inventário de referências locais](../arquivos-somente-locais.json). Não houve commit nem push nesta tarefa.
