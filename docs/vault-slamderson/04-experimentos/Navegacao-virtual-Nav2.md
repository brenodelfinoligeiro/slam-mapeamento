# Navegação virtual Nav2

[Galeria pública do ensaio](../../navegacao/imagens/LEIA-ME.md): gráficos de trajeto e métricas produzidos de dados observados, com fonte SVG e dados reproduzíveis, sem geometria CAD. A captura RViz e os pacotes com derivados de licença pendente permanecem somente locais; o pedido de publicação não altera essa restrição.

## Resultado observado

Nav2 Jazzy real, não publicador sintético autônomo: três ações NavigateToPose concluíram com SUCCEEDED e error_code zero, passando pela proteção e árbitro até rodas/planta. A reta para o primeiro objetivo cruza uma caixa; o percurso real a contornou. O oráculo independente audita segmentos entre poses e envoltória circular de 0,18 m, mais margem de amostragem.

Cancelamento em movimento, tomada manual e perdas de scan, TF global, odometria e clock foram exercitados em namespace isolado de PID, com retomada dos processos garantida. Falhas cancelaram ações e travaram parada; recuperação/rearme não ressuscitou objetivo antigo. Objetivo fora do mapa terminou ABORTED. O cliente público ir_para também foi exercitado em sessão nova, iniciando em manual.

[Relatório executado](../../navegacao/validacao-navegacao.json) identifica repetições, contagens e ensaios aprovados de recarga/RViz e encerramento lifecycle ordenado. Contagens não somam wrappers CTest ou execuções repetidas. Nenhum teste mede comportamento físico; pausar clock também congela a planta virtual, logo deslocamento zero nesse caso não prova frenagem real.

[[03-decisoes/Navegacao-Nav2-arbitrada]] · [[04-experimentos/Arbitragem-manual-autonoma]] · [[04-experimentos/SLAM-virtual-e-localizacao]] · [[Inicio]]

A suíte final tem 503 casos dos pacotes e 10 do oráculo/helpers (513 sem wrappers ou repetições). O helper público também foi operado por PTY real, com Ctrl+C ordenado e remoção do contêiner. A imagem final apresenta Global Status Ok; não é prova de resultado da ação. O encerramento correto usa SHUTDOWN/readback antes de sinais aos processos, pois SIGINT direto no SLAM ativo revelou aborto upstream.
