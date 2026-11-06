# Publicação no GitHub

## Repositório

Remoto autorizado pelo autor: <https://github.com/brenodelfinoligeiro/slam-mapeamento>, branch `main`. O commit inicial e o README do proprietário são preservados; o workspace local continua em `robo_movel_ws` e o pacote atual se chama `robo_movel`.

A documentação detalhada continua em [LEIA-ME.md](LEIA-ME.md). A publicação não implementa nós de hardware nem comprova ROS 2, UART, LiDAR ou movimento em funcionamento.

## Conteúdo publicado e referências somente locais

Código, testes, documentação própria, referências bibliográficas, metadados de procedência e avisos de licença são versionados. Os CADs da Raspberry Pi 5, motor Adafruit 3777, MPU-6050 e L298N são incluídos com os avisos MIT/CC BY identificados no catálogo. Isso não licencia automaticamente o código próprio nem outros arquivos do projeto.

Permanecem somente na cópia local, sem exclusão física:

- CADs sem licença identificada e modelos com cadeia de autoria/licença de componentes importados ou remixes ainda não esclarecida, inclusive o chassi.
- Prévias que reproduzem esses modelos, fotografias de terceiros, PDFs e cópias integrais de páginas/textos de fabricantes cuja autorização de redistribuição não foi estabelecida.
- Saídas de compilação, instalação, logs, caches, credenciais e estado pessoal do editor.

[arquivos-somente-locais.json](arquivos-somente-locais.json) relaciona as referências omitidas, seus hashes originais e a justificativa. Os manifestos de CAD/PDF preservam o inventário da coleção local: **não são listas de arquivos necessariamente distribuídos pelo Git**. Links desses catálogos e notas para caminhos relacionados no inventário funcionam apenas na cópia local completa. Na cópia pública, consultar a URL de origem indicada no manifesto; não há download automático nem autorização implícita de redistribuição.

## Malhas ROS derivadas

As malhas de tempo de execução em `src/descricao/robo_movel/descricao/malhas/` são derivadas do CAD local e não recebem licença nova pelo fato de serem instaladas como recurso ROS. Permanecem ignoradas, com hashes/motivos no [inventário específico](descricao-ros/malhas-somente-locais.json). Não usar `git add -f` para publicá-las. A visualização e seus novos testes geométricos exigem restaurar esses recursos; uma cópia pública só com código não equivale ao pacote local completo.

## Imagens e escopo da atualização Nav2

O pedido atual do autor autoriza a publicação do código, testes e documentação própria acumulados, incluindo os doze pacotes ROS. A [galeria pública](navegacao/imagens/LEIA-ME.md) contém gráficos de telemetria sintética observada, SVGs/PNGs e dados de entrada; não reproduz malhas ou modelos CAD. A captura RViz com CAD e os arquivos de atualização com derivados pendentes continuam locais, sem forçar inclusão de ignorados. Os recibos anteriores que dizem “sem commit/push” descrevem o momento dos respectivos ensaios; não são o estado desta publicação posterior.

**A cópia pública não é o workspace completo executável entregue localmente.** Faltam as malhas intencionalmente retidas e mapas/grafos locais. O ensaio de 513 casos foi executado sobre a cópia local completa, com os hashes registrados no recibo. Clonar o Git não restaura automaticamente esses recursos nem resolve sua licença. Nenhum deploy ou teste físico é autorizado pela publicação.

## Validação em uma cópia clonada

```bash
cd src/descricao/robo_movel
uv run --no-project --with pytest==9.2.0 python -m pytest -p no:cacheprovider -q testes \
  -k 'not teste_malhas_em_metros_resolvem_e_preservam_hashes_e_facetas'
```

Na cópia pública verificada, os 17 testes restantes passaram. O teste de integridade das malhas fica **explicitamente fora desse recorte**, pois exige os 18 STL retidos. Executar a suíte integral no Git público sem restaurá-los produz 17 aprovados e 1 falha por recurso ausente; a falha foi observada e não foi escondida enfraquecendo o teste. Na cópia local completa, os 18 testes passaram. Esse recorte documental não equivale aos 513 casos ROS/oráculo executados anteriormente.

Os testes conferem bytes e hashes de todas as referências presentes. Quando uma referência foi omitida do Git, exigem sua identificação exata no inventário de arquivos somente locais, com hash e justificativa. Uma ausência não declarada ou um arquivo presente adulterado continua sendo erro. O mesmo vale para links locais: somente alvos explicitamente inventariados podem estar ausentes da publicação.

Não existe licença geral escolhida para o projeto. Os avisos de terceiros continuam aplicáveis individualmente; uma licença geral não foi presumida durante a publicação.
