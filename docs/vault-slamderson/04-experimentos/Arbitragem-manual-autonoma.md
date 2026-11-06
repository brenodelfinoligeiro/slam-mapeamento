# Ensaio digital de arbitragem

O pacote foi exercitado em ROS/DDS real no contêiner Jazzy do Xeon. Fontes manual e autônoma publicaram simultaneamente; somente a origem selecionada chegou à base. Foram verificados troca neutra, ausência de fallback, parada travada, replay/NaN, expiração, manutenção do carimbo, watchdog com clock pausado, teclado remapeado por PTY e reinício completo no modo manual.

Os comandos autônomos são estímulos de teste, não saída de um Nav2 implementado. Não é ensaio de sensores, obstáculos, acionamento ou navegação físicos. Os recibos e a contagem estão no relatório do recorte, sem somar wrapper CTest.

[Guia e limites](../../arbitro/LEIA-ME.md) · [[03-decisoes/Arbitro-de-movimento]] · [[Inicio]]
