---
tipo: experimento
estado: exercitado_em_ROS_isolado
atualizado: 2026-11-05
---
# Descrição ROS da montagem R05

O autor pediu usar o modelo 3D como `robot_description`. A montagem nativa R05 foi exportada por folhas, sem duplicar compostos e sem usar orientações dos STL de impressão. URDF e recursos ficam no pacote `slamderson`; [procedimento completo](../../descricao-ros/LEIA-ME.md).

- 44 instâncias impressas, referências e ferragens agrupadas em 18 malhas visuais; 7 links e 2 juntas contínuas de rodas.
- Conversão CAD mm para ROS m, rotação própria sem reflexão; frente CAD −Y vira +X ROS.
- Instalação, `check_urdf`, 16 testes colcon e TFs de duas rodas com ângulos de ensaio executados em contêiner ROS 2 Jazzy sem rede/dispositivos. RViz real exibiu Global Status OK.
- O launch `descricao.launch.py` não publica juntas fictícias; o de visualização é demonstração. Sem UART, motores ou sensores reais.
- Datums IMU/C1 não são extrínsecas calibradas. Inércias/limites de acionamento não foram inventados. Rodízio fixo para visualização; sua referência geométrica está 5,313 mm acima do plano inferior dos pneus, sem correção artificial.
- No ensaio gráfico, SIGINT com RViz aberto falhou ao encerrar. Fechar a janela primeiro e depois o launch foi verificado limpo; isso não prova a causa da falha de SIGINT corrigida.

[[03-decisoes/Arquitetura-atual]] · [[01-componentes/Suporte-C1]] · [[01-componentes/MPU-6050]]
