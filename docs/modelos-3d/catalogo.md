# Modelos 3D — Slamderson

Coleção de arquivos CAD públicos preexistentes para estudo de montagem. **Importação válida não significa correspondência à peça física nem desenho certificado para fabricação.** Nenhum arquivo foi publicado ou enviado a um repositório remoto.

## Escolha rápida

- **Pi 5:** priorizar o ZIP oficial, contendo STEP e licença. Extrair antes de abrir no CAD. A versão sem gráficos foi preservada para evitar o arquivo oficial alternativo de 142 MB.[11]
- **C1:** arquivo identificado como C1M1 V2 de 2023, obtido pela DFRobot. Inclui acessórios/geometria estendida; o envelope global não representa somente o corpo do sensor. A licença do CAD não foi identificada.[12]
- **Motor TT:** referência Adafruit 3777, não identificação dos motores instalados. Conferir ambos os extremos do eixo, perfil, projeção, furos e medidas. A redução do produto fonte não é a redução medida do carrinho.[13]
- **L298N:** preferir `l298n-freecad-library.step`, com arquivo nativo FreeCAD adicional. Trata-se de modelo de módulo comercial, não de nova placa de acionamento do projeto.[14][18]
- **MPU-6050:** placa candidata visualmente compatível com a família GY-521; a revisão física do módulo do autor continua desconhecida.[15]
- **Encoder:** foi preservada uma montagem pública e exportado dela o componente `Interrupt Sensor v1`.[19] Após examinar a prévia, o autor confirmou visualmente que é o encoder do projeto. A identificação visual não comprova medidas, furação ou características elétricas nem identifica automaticamente o circuito integrado como LM393.
- **ESP:** modelos C3 SuperMini e ESP32S HW-573 estão separados em `candidatos/`; não alteram a escolha ainda pendente do microcontrolador. O C3 tem envelope incomum e não é recomendado como referência dimensional sem investigação.[16][17]

## Arquivos

- **Raspberry Pi 5 Model B** — [rpi-5-no-graphics.zip](arquivos/raspberry-pi-5/rpi-5-no-graphics.zip); referência a conferir; verificação: `importado`.[11]
- **RPLIDAR C1 / C1M1** — [C1M1_appearance_V2_20230926.3d_model.stp](arquivos/lidar-c1/C1M1_appearance_V2_20230926.3d_model.stp); referência a conferir; verificação: `importado`.[12]
- **Motorredutor TT, referência Adafruit 3777** — [3777 TT Motor.f3d](arquivos/motor-tt/3777%20TT%20Motor.f3d); referência a conferir; verificação: `nao_inspecionado`.[13]
- **Motorredutor TT, referência Adafruit 3777** — [3777 TT Motor.step](arquivos/motor-tt/3777%20TT%20Motor.step); referência a conferir; verificação: `importado`.[13]
- **Motorredutor TT, referência Adafruit 3777** — [3777 TT Motor.stl](arquivos/motor-tt/3777%20TT%20Motor.stl); referência a conferir; verificação: `importado`.[13]
- **Módulo L298N** — [l298n-freecad-library.step](arquivos/l298n_step/l298n-freecad-library.step); referência a conferir; verificação: `importado`.[14]
- **Placa MPU-6050 candidata** — [mpu6050-placa-candidata.step](arquivos/mpu6050/mpu6050-placa-candidata.step); referência a conferir; verificação: `importado`.[15]
- **ESP32-C3 SuperMini, candidato não escolhido** — [esp32-c3-supermini-candidato.stp](candidatos/esp32_c3_candidato/esp32-c3-supermini-candidato.stp); candidato opcional; verificação: `importado`.[16]
- **ESP32S HW-573, candidato não escolhido** — [esp32s-devboard-candidato.step.zip](candidatos/esp32s_candidato/esp32s-devboard-candidato.step.zip); candidato opcional; verificação: `importado`.[17]
- **Módulo L298N, arquivo nativo** — [L298N.FCStd](arquivos/l298n_step/L298N.FCStd); referência a conferir; verificação: `nao_inspecionado`.[18]
- **Sensor óptico candidato, montagem de origem** — [Robot.step](referencias/sensor-candidato/Robot.step); referência em montagem; verificação: `importado`.[19]
- **Sensor óptico LM393 candidato extraído** — [sensor_lm393_candidato_extraido.step](arquivos/sensor-candidato/sensor_lm393_candidato_extraido.step); referência a conferir; verificação: `importado`.[19]

## Chassi B — pacote fornecido pelo usuário

O usuário baixou o pacote Thingiverse 4738179 de dasaki; ele foi copiado dos Downloads do Ryzen para o projeto e conferido por SHA-256, preservando o original remoto. O pacote identifica o autor como dasaki e declara GNU-GPL, sem informar a versão; o README lista várias fontes de remix, cujas condições não foram auditadas.[22]

- [ZIP original — montagem completa](arquivos/chassi-2wd-B/2WD%20smart%20car%20arduino%20robot%20chassis%20-%204738179.zip). Extrair o ZIP externo e depois `files/2wd_robot.zip`; os originais internos são `2wd_robot.blend` e `2wd_robot.stl`, não STEP.
- [Base e suportes — STL derivado](arquivos/chassi-2wd-B/chassi_e_suportes_derivado_mm.stl).
- [Rodízio — STL derivado](arquivos/chassi-2wd-B/rodizio_derivado_mm.stl).

O Blender original foi aberto no Ryzen com execução automática de scripts desabilitada. A cena usa sistema métrico e escala de aproximadamente 0,001 metro por unidade; os derivados mantêm essas coordenadas, interpretadas como milímetros. O STL não codifica unidade por si mesmo. A montagem STL e os dois derivados foram importados pelo FreeCAD. O ZIP original foi mantido para evitar acrescentar o STL ASCII de aproximadamente 126 MB descompactado ao projeto.

A inspeção visual encontrou a família da base B: ponta arredondada, abertura circular, rasgos, motores/rodas e rodízio. Isso não valida medidas ou o padrão exato de todos os furos da peça real. A base extraída inclui suportes; seu envelope vertical não é a espessura da chapa. Os objetos derivados não foram remodelados, reparados ou redimensionados; a seleção e a exportação estão registradas no manifesto.

![Prévia original da montagem fornecida](previas/chassi-4738179-original-1.png)

## Organização e licenças

- `arquivos/`: modelos de referência para os componentes do projeto.
- `candidatos/`: alternativas de microcontrolador ainda não escolhidas.
- `referencias/`: montagem original que contém o sensor óptico candidato; não é um modelo do robô Slamderson.
- `licencas/`: avisos originais preservados.
- `fontes/`: metadados de pesquisa, textos originais de procedência e desenho mecânico complementar.
- `validacoes/`: resultados por arquivo.
- `previas/`: prévias identificadas; a prancha usa malhas simplificadas somente para visualização.
- [Manifesto completo](manifesto.json): origem, download, autoria, licença, hash, tamanho, correspondência e inspeção geométrica.
- [Bibliografia CAD](referencias.bib).

MIT e CC BY são identificadas apenas onde existe aviso aplicável preservado. A licença CC BY-SA do projeto de origem do sensor é declarada para o CAD/documentação, mas a autoria/licença original de componentes importados na montagem não foi esclarecida. Onde a licença permanece desconhecida, o arquivo foi guardado como referência local: **não presumir autorização para publicar ou redistribuir**.

A Pi 5 e o ESP32S estão compactados para reduzir o peso da coleção. O ZIP da Pi é o download original; o do ESP32S foi criado localmente sem alterar os bytes do STEP interno. Os originais de CAD não foram reparados ou redimensionados. O sensor extraído é uma derivação declarada do arquivo `Robot.step`, com seu hash de origem no manifesto.

## Validação realmente executada

Na primeira coleta, a inspeção do mantenedor importou nove geometrias STEP, incluindo o STEP contido no ZIP da Pi, e uma malha STL no FreeCAD 1.1.4. Oito STEP retornaram geometria válida. A montagem completa de origem do sensor é importável, mas falha em `isValid()` e foi marcada **somente para procedência**, não para montagem: o sensor extraído isoladamente passou na validação. Os arquivos nativos F3D/FCStd tiveram sua estrutura ZIP e CRC verificados, mas não foram exercitados nos aplicativos nativos como parte dessa inspeção.

Duas alternativas L298N eram cópias idênticas geometricamente inválidas e foram rejeitadas; seus registros constam no manifesto, não na coleção de modelos utilizáveis. Nenhuma fabricação, medição física, compatibilidade de furação ou configuração de colisão ROS foi validada.

## Pendências

- Conferir medidas e furação do modelo do encoder, cuja identificação visual foi confirmada pelo autor.
- Obter disco encoder TT avulso com correspondência confirmada.
- Conferir as medidas e a furação reais do chassi B e do rodízio de referência; identificar revisões de rodas, bateria e acessórios antes de tratá-los como geometrias exatas.
- Conferir dimensões e revisões reais antes de projetar suportes.
- Para URDF, selecionar subcorpos, definir origem, orientar e converter corretamente para metros; não usar automaticamente todo o STEP como colisão.

## Prévia

![Prancha de referências CAD](previas/colecao-cad.png)

As escalas entre quadros são independentes. A prévia não é uma montagem do robô nem prova de encaixe.

## Sources

[11] https://pip.raspberrypi.com/documents/RP-010083-CA — CAD — Raspberry Pi 5 Model B
[12] https://www.dfrobot.com/product-2803.html — CAD — RPLIDAR C1 / C1M1
[13] https://github.com/adafruit/Adafruit_CAD_Parts/tree/main/3777%20TT%20Motor — CAD — Motorredutor TT, referência Adafruit 3777
[14] https://github.com/FreeCAD/FreeCAD-library/blob/71fae7e9bd207078f3dc27efadd7a02da7e2efee/Electrical%20Parts/Motor%20Drivers/L298N/L298N.step — CAD — Módulo L298N
[15] https://github.com/racerxdl/kicad-board-collection/blob/8477c32b6a499361b55bfec1312e5a8a899caf05/MPU6050/MPU6050.step — CAD — Placa MPU-6050 candidata
[16] https://github.com/NerdyProjects/conti_bat_trigger/blob/2b7375378fdefbd9b49d89daa44583d2694571cc/hw/KiCad_ESP32-C3-SuperMini/ESP32-C3-SuperMini.stp — CAD — ESP32-C3 SuperMini, candidato não escolhido
[17] https://github.com/Mayoogh/KiCAD-Custom-Libraries-/blob/71b1199b1863b1d4ce4d9fbe3ff4cc628c93054a/Development%20board/Espressif%20Systems/ESP32/ESP32S%20Dev%20Board.STEP — CAD — ESP32S HW-573, candidato não escolhido
[18] https://github.com/FreeCAD/FreeCAD-library/blob/71fae7e9bd207078f3dc27efadd7a02da7e2efee/Electrical%20Parts/Motor%20Drivers/L298N/L298N.FCStd — CAD — Módulo L298N, arquivo nativo
[19] https://github.com/pserey/SimpleTTRobot — CAD — Sensor óptico LM393 candidato extraído
[22] https://www.thingiverse.com/thing:4738179 — dasaki — 2WD smart car arduino robot chassis; pacote fornecido pelo autor do projeto
