---
tipo: componente
estado: cad_referencia_recebido_e_inspecionado
---
# Chassi maker 2WD

## Informação do autor

O autor informou que o carrinho usa chassi maker 2WD padrão, com duas rodas motoras e um rodízio, e selecionou explicitamente a **foto B**, de base com abertura circular, na prancha de comparação. Confirmação registrada pela mensagem `1567625934830444557`. Dimensões, espessura e posição exata dos furos ainda precisam de conferência física; a escolha visual não identifica fabricante ou revisão comercial.

## Referências visuais

A [prancha de comparação](../../modelos-3d/referencias/chassi-2wd/comparacao-2wd.jpg) contém três fotos identificadas por letra, não três modelos necessariamente distintos:

- **A:** vista inferior de um kit anunciado pela Casa da Robótica, com rodízio claramente visível.[20]
- **B:** foto de anúncio Arduino e Cia, destacando base com abertura circular.[21]
- **C:** outra foto da mesma página Arduino e Cia, com disposição de rasgos visualmente diferente.[21]

Não afirmar que as fotos B e C são o mesmo recorte só por estarem na mesma página de produto. São referências comerciais para identificação visual, não desenhos dimensionais ou modelos CAD certificados. Não foi verificada disponibilidade em estoque.

Originais, URLs de página e de imagem, dimensões em pixels e hashes estão em [fontes-imagens.json](../../modelos-3d/referencias/chassi-2wd/fontes-imagens.json). As fotografias são de terceiros; não foi identificada licença aberta. Foram mantidas com atribuição para comparação visual.

## Busca do CAD correspondente

A busca HTTP inicial foi bloqueada por respostas 403 de GrabCAD e Thingiverse. Depois, o usuário baixou o pacote Thingiverse 4738179 de dasaki e o disponibilizou nos Downloads do Ryzen. A cópia para o projeto foi conferida por SHA-256, sem remover ou alterar o ZIP remoto. O arquivo identifica dasaki e declara GNU-GPL, sem especificar versão; o README indica remixes de outras fontes.[22]

O pacote contém outro ZIP, com STL e Blender da montagem mecânica completa. As prévias e a geometria apresentam a família visual B, com abertura circular, rodas/motores e rodízio. O Blender foi aberto no Ryzen com execução automática desabilitada; sua cena métrica indica escala de aproximadamente 0,001 metro por unidade. A montagem e os derivados foram importados pelo FreeCAD. Isso não confirma a furação exata ou medidas da peça física.

Arquivos preservados na pasta local `docs/modelos-3d/arquivos/chassi-2wd-B/`, não distribuída pelo Git por pendências de licença; consulte a [política de publicação](../../publicacao-git.md):

- ZIP original preservado, incluindo README, declaração de licença e os originais STL/Blender.
- `chassi_e_suportes_derivado_mm.stl`: exportação do objeto existente `RobotChassis.001`; inclui suportes, não apenas a chapa plana.
- `rodizio_derivado_mm.stl`: exportação do objeto existente `Caster`.

Os derivados mantêm as coordenadas do modelo, sem remodelagem ou redimensionamento. Os limites de licença dos componentes de remix não foram auditados; não presumir autorização uniforme de redistribuição. O histórico de bloqueios e rejeições está em [busca-cad-b.json](../../modelos-3d/referencias/chassi-2wd/busca-cad-b.json).

## Próxima identificação necessária

Conferir contorno, rasgos, medidas e furos do CAD recebido contra o chassi real antes de projetar suportes. Não confundir o envelope vertical da base com suportes com a espessura da chapa, nem as posições da montagem com transformações ROS calibradas. Fotografias continuam separadas do inventário CAD.

[[01-componentes/Modelos-3D]] · [[03-decisoes/Arquitetura-atual]]

## Sources

[20] https://www.casadarobotica.com/robotica/chassi-s/carros/kit-chassi-2-rodas — Casa da Robótica — kit chassi 2 rodas: fotos de referência
[21] https://arduinoecia.com.br/produto/kit-chassi-2wd-robo-para-arduino — Arduino e Cia — kit chassi 2WD: fotos de referência
[22] https://www.thingiverse.com/thing:4738179 — dasaki — 2WD smart car arduino robot chassis; pacote fornecido pelo autor do projeto
