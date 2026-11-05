---
tipo: modelos_mecanicos
estado: referencias_coletadas_correspondencia_fisica_pendente
atualizado: 2026-11-04
---
# Modelos 3D das peças

Os originais e derivados declarados estão no [catálogo da coleção](../../modelos-3d/catalogo.md), fora dos recursos de execução do pacote ROS. O [manifesto](../../modelos-3d/manifesto.json) registra procedência, licenças, formatos e validações.

## Correspondência e uso

- Pi 5: arquivo oficial Pi 5B, sem confirmação de revisão física ou RAM específica.[11]
- C1: aparência C1M1 V2 fornecida pela DFRobot; acessórios ampliam o envelope da montagem, não usar o total como corpo isolado do LiDAR.[12]
- TT: CAD Adafruit 3777, apenas referência de família; não determina redução ou dimensões dos motores reais.[13]
- L298N: referência comunitária de módulo completo, com STEP e arquivo nativo FreeCAD.[14][18]
- MPU-6050: placa candidata, não confirmação da placa física.[15]
- Chassi 2WD: pacote Thingiverse 4738179 de dasaki recebido pelo usuário, com originais STL/Blender; base com suportes e rodízio foram exportados separadamente.[22] Família visual compatível com a foto B, mas medidas e furação física permanecem a conferir.
- Sensor óptico: modelo extraído da montagem SimpleTTRobot.[19] O autor confirmou visualmente que é o encoder do projeto; medidas e características elétricas ainda não foram verificadas. A montagem de origem não representa o carrinho.
- ESP32-C3 SuperMini e ESP32S: opções ainda não escolhidas; o arquivo C3 possui envelope suspeito e não deve orientar suporte sem inspeção.[16][17]

## Fronteira entre CAD e evidência física

Abertura em kernel CAD, validade topológica e hash verificam o arquivo, não o encaixe na peça real. Conferir medidas, furação, conectores, extremos dos eixos e volume livre necessário aos cabos. Não tratar STL sem unidade declarada como se estivesse em metros.

A montagem original usada como fonte do sensor falha na verificação topológica global e foi preservada somente como procedência. O sensor isolado exportado dessa montagem tem geometria válida e correspondência visual confirmada pelo autor; isso não comprova precisão dimensional. A classificação negativa da montagem está explícita no manifesto.

Os modelos oficiais/autorais com licença identificada têm os avisos preservados. Arquivos sem licença explícita não devem ser publicados ou redistribuídos presumindo autorização. A licença de um repositório não foi aplicada automaticamente ao CAD de terceiro.

## O que falta

O autor informou chassi maker 2WD com duas rodas motoras e um rodízio. As [[01-componentes/Chassi-2WD|fotos de comparação]] ajudam a identificar recorte e furação; não são modelos CAD.

Conferência dimensional do modelo do encoder e obtenção de disco encoder TT avulso confirmado. O chassi não estava na rodada inicial, mas agora há montagem de referência da família B e rodízio derivado, descritos em [[01-componentes/Chassi-2WD]]. Conferir medidas, furação e revisões físicas de chassi, rodas e rodízio; a bateria ainda precisa ser identificada. A escolha de ESP permanece pendente; os downloads não fecham essas decisões.

## Relações

[[01-componentes/Encoder-MH-Sensor-Series]] · [[01-componentes/L298N]] · [[01-componentes/MPU-6050]] · [[03-decisoes/Arquitetura-atual]] · [[06-ideias/Ideias-e-pendencias]]

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
