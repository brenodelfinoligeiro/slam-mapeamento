---
tipo: indice
projeto: robo_movel
atualizado: 2026-11-07
---
# Robô móvel — base de conhecimento

**Monografia e software:** [[05-fontes/Software-e-monografia|referências, leitura prioritária e ligação com a implementação]].

**SLAM/localização em simulação:** [[04-experimentos/SLAM-virtual-e-localizacao]], [[03-decisoes/SLAM-localizacao-antes-da-navegacao]] e [guia operacional](../slam/LEIA-ME.md). Mapeamento e recarga de grafo; integração Nav2 registrada abaixo; hardware permanece pendente.

**Descrição ROS do CAD:** [URDF, launches e validação Jazzy](../descricao-ros/LEIA-ME.md) e [[04-experimentos/Descricao-ROS-R05|ensaio em RViz/TF]].

**Mecânica mais recente:** [[01-componentes/Insertos-e-retencoes|R05 com insertos M3 e retenções rígidas]], [kit/STL/validações](../fixacao-r05/LEIA-ME.md) e [manual R05 de montagem e seis vistas](../fixacao-r05/slamderson-r05-montagem-e-seis-vistas.pdf). Protótipo dimensional; cupom e conferência física antes do lote.

Este vault reúne pesquisa bibliográfica, ideias, decisões e procedimentos do trabalho acadêmico. Abrir **esta pasta** como um vault no Obsidian. Não depende de plugins comunitários nem de serviços pagos.

## Começar por aqui

- [[00-organizacao/Como-manter-o-vault|Como manter o conhecimento atualizado]].
- [[00-organizacao/Criterios-de-confiabilidade|Critérios de confiabilidade e citação]].
- [[00-organizacao/Validacao-do-vault|Validação dos arquivos e limites da entrega]].
- [[01-componentes/Encoder-MH-Sensor-Series|Encoders MH-Sensor-Series: o que sabemos e o que falta confirmar]].
- [[01-componentes/L298N|Módulo L298N]].
- [[01-componentes/MPU-6050|MPU-6050]].
- [[01-componentes/Powerbank-Basike|Powerbank real Basike: medidas, massa indicada e etiqueta elétrica]].
- [[01-componentes/Modelos-3D|Modelos 3D, procedência e limites de correspondência]].
- [[01-componentes/Chassi-2WD|Chassi maker 2WD: fotos para identificar recorte e furação]].
- [Disposição dos componentes em vistas 2D, com quatro AA](../disposicao-2d/LEIA-ME.md): estudo de envelopes e suportes propostos, não desenho de fabricação.
- [R03 — montagem coberta com suporte C1 compacto](../carcaca-r03/LEIA-ME.md): base reduzida a 62 × 62 mm, preservando Basike real e retirada das tampas. [[01-componentes/Suporte-C1|Detalhes e limites do suporte]]. [R02](../carcaca-r02/LEIA-ME.md) e [R01 aberto](../montagem-3d/LEIA-ME.md) preservados como históricos.
- [[02-fundamentos/Contagem-e-odometria|Contagem de pulsos e odometria]].
- [[03-decisoes/Arquitetura-atual|Decisões atuais de arquitetura]].
- [[04-experimentos/Caracterizacao-dos-encoders|Procedimento proposto para caracterizar os encoders]].
- [[05-fontes/Catalogo-de-fontes|Fontes, PDFs, limitações e falhas de acesso]].
- [[06-ideias/Ideias-e-pendencias|Ideias e pendências]].

## Publicação no GitHub

O remoto autorizado é <https://github.com/brenodelfinoligeiro/slam-mapeamento>. A [política de publicação](../publicacao-git.md) distingue arquivos versionados de referências mantidas somente na coleção local; a existência de um caminho no catálogo não comprova sua distribuição pelo Git.

## Uso junto aos capítulos do projeto

Os capítulos em `docs/` continuam sendo a apresentação consolidada do projeto. O vault é a base interligada de pesquisa e desenvolvimento; não é uma segunda versão concorrente da arquitetura. Atualizar os resumos dos capítulos quando uma conclusão mudar.

Identificar sempre **fato informado pelo autor**, **documentação de fabricante**, **informação comercial**, **hipótese** e **resultado medido**. Nenhum ensaio físico foi executado nesta pesquisa.

## Achado que exige atenção

O manual de um módulo semelhante contém inconsistências elétricas e um exemplo incorreto de RPM. Veja [[05-fontes/notas/Fonte-02-Whadda-WPSE347|a análise crítica]], antes de utilizar seus números.

## Identidade do software ROS

[[03-decisoes/Identidade-generica-ROS]]: pacote atual `robo_movel`, workspace `robo_movel_ws`; doze pacotes funcionais nos cinco agrupadores. Nav2 foi integrado ao recorte virtual; ponte UART e C1 físico permanecem propostos.

## Árbitro de movimento

[[03-decisoes/Arbitro-de-movimento]] · [[04-experimentos/Arbitragem-manual-autonoma]].

## Simulação funcional

[[04-experimentos/Simulacao-odometria-IMU-teleop]]: recorte com sensores virtuais e teleop exercitado no Xeon, sem hardware.

## Navegação autônoma virtual

[[03-decisoes/Navegacao-Nav2-arbitrada]] · [[04-experimentos/Navegacao-virtual-Nav2]] · [Guia operacional](../navegacao/LEIA-ME.md).
