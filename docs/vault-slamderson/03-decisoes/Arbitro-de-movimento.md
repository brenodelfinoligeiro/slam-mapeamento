# Árbitro de movimentação

## Decisão do autor

Separar manual/autônomo num pacote `arbitro`, dentro de `src/navegacao`, antes de concluir a integração de navegação autônoma.

## Contrato implementado

TwistStamped manual/autônomo em entradas separadas; saída única /cmd_vel para o consumidor existente. Seleção explícita por SetBool, parada travada por Trigger, estado JSON/String latched. Default manual; troca abre época e exige comando novo. Não há mistura, fallback automático ou renovação por replay. Prazo ROS e monotônico, timer steady, clock regressivo exige rearmar.

Não controla objetivos Nav2, nem sensores/SLAM ou segurança física. O coordenador futuro deve tratar cancelamento de ação ao tomar controle manual. Nenhum hardware, deploy ou publicação foi executado.

[Interfaces e comandos](../../arbitro/LEIA-ME.md) · [[04-experimentos/Arbitragem-manual-autonoma]] · [[03-decisoes/Arquitetura-atual]] · [[Inicio]]
