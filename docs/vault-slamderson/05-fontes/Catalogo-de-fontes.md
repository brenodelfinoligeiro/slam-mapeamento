---
tipo: catalogo
consulta: 2026-11-04
---
# Catálogo de fontes

- [ROS: descrição, unidades e transformações](Descricao-ROS.md) — fontes oficiais ROS-REP103 e ROS-RSP-JAZZY, aplicadas ao URDF R05.

## Referências efetivamente consultadas

- Fonte 1 — [[05-fontes/notas/Fonte-01-Einstronic-MH|Einstronic: MH Infrared Speed Sensor Module]]. Página comercial, sem PDF primário localizado. Sustenta associação de nomes, não identificação elétrica final.[1]
- Fonte 2 — [[05-fontes/notas/Fonte-02-Whadda-WPSE347|Whadda/Velleman WPSE347]]. PDF do responsável por **outro módulo semelhante**, com inconsistências explicitamente analisadas.[2]
- Fonte 5 — [[05-fontes/notas/Fonte-05-TI-LM393|Texas Instruments LM393]]. Datasheet obtido do fabricante, aplicável ao comparador se ele for confirmado na placa.[5]
- Fonte 7 — [[05-fontes/notas/Fonte-07-InvenSense-Registradores|InvenSense: mapa de registradores]]. Documento de fabricante em cópia SparkFun.[7]
- Fonte 8 — [[05-fontes/notas/Fonte-08-ST-L298|STMicroelectronics L298]]. Documento de fabricante em hospedagem TremTech; não houve comparação com download oficial.[8]
- Fonte 10 — [[05-fontes/notas/Fonte-10-InvenSense-Especificacao|InvenSense: especificação MPU-6050]]. Revisão 3.3, cópia DFRobot, sem afirmação de atualidade.[10]
- Fonte 23 — Raspberry Pi Ltd, [USB Power Delivery on Raspberry Pi 5](https://pip.raspberrypi.com/documents/RP-009856-WP). O resumo indexado oficial recomenda 5 V/5 A e admite 3 A com periféricos de baixa potência; a evidência local é o resultado da busca, não extração integral do PDF.[23]

## Coletas que falharam

As falhas desta seção pertencem à pesquisa inicial dos módulos. A pesquisa posterior de CAD tem seus próprios registros e limitações no [catálogo de modelos 3D](../../modelos-3d/catalogo.md), referenciado em [[01-componentes/Modelos-3D]].

Os identificadores 3 e 4 correspondem a endereços ST com tempo de resposta excedido; 6 corresponde ao PDF TDK com HTTP 403; 9 corresponde ao endereço SparkFun com HTTP 404. Os endereços exatos e os erros estão em `registros-coleta/` e `manifesto-arquivos.json`. Não há arquivo local inventado para esses acessos.

## Auditoria e reutilização acadêmica

- [[05-fontes/manifesto-arquivos.json|Manifesto dos arquivos e acessos]]: endereço solicitado, endereço de download, data/hora, tipo, páginas e SHA-256.
- [[05-fontes/citacoes.json|Registro de referências e trechos literais]]: identificadores estáveis usados nas notas.
- [[05-fontes/referencias.bib|Entradas BibTeX iniciais]]: base de importação, não certificação de formatação ABNT.
- PDFs originais em `pdf/`; textos extraídos para verificação em `evidencias/`. Não confundir a extração de texto com o documento original.

Os documentos de terceiros e seus avisos de autoria foram preservados. Este catálogo não atribui às placas do carrinho características de outro produto. Consulte [[00-organizacao/Criterios-de-confiabilidade]] e [[01-componentes/Encoder-MH-Sensor-Series]].

## Sources

[1] https://einstronic.com/product/infrared-speed-sensor-module — Einstronic — MH Infrared Speed Sensor Module
[2] https://cdn.velleman.eu/downloads/25/wpse347a4v01.pdf — Velleman — WPSE347: IR speed sensor module
[5] https://www.ti.com/lit/ds/symlink/lm393.pdf — Texas Instruments — LM393: Dual Comparators
[7] https://cdn.sparkfun.com/datasheets/Sensors/Accelerometers/RM-MPU-6000A.pdf — InvenSense — MPU-6000/MPU-6050 Register Map; cópia SparkFun
[8] https://store.tremtech.com/content/l298.pdf — STMicroelectronics — L298; cópia hospedada pela TremTech
[10] https://dfimg.dfrobot.com/enshop/image/data/SEN0142/PS-MPU-6000A.pdf — InvenSense — MPU-6000/MPU-6050 Product Specification; cópia DFRobot
[23] https://pip.raspberrypi.com/documents/RP-009856-WP — Raspberry Pi Ltd — USB Power Delivery on Raspberry Pi 5
