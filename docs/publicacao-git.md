# Publicação no GitHub

## Repositório

Remoto autorizado pelo autor: <https://github.com/brenodelfinoligeiro/slam-mapeamento>, branch `main`. O commit inicial e o README do proprietário são preservados; o workspace local continua em `slamderson_ws` e o pacote mantém o nome `slamderson`.

A documentação detalhada continua em [LEIA-ME.md](LEIA-ME.md). A publicação não implementa nós de hardware nem comprova ROS 2, UART, LiDAR ou movimento em funcionamento.

## Conteúdo publicado e referências somente locais

Código, testes, documentação própria, referências bibliográficas, metadados de procedência e avisos de licença são versionados. Os CADs da Raspberry Pi 5, motor Adafruit 3777, MPU-6050 e L298N são incluídos com os avisos MIT/CC BY identificados no catálogo. Isso não licencia automaticamente o código próprio nem outros arquivos do projeto.

Permanecem somente na cópia local, sem exclusão física:

- CADs sem licença identificada e modelos com cadeia de autoria/licença de componentes importados ou remixes ainda não esclarecida, inclusive o chassi.
- Prévias que reproduzem esses modelos, fotografias de terceiros, PDFs e cópias integrais de páginas/textos de fabricantes cuja autorização de redistribuição não foi estabelecida.
- Saídas de compilação, instalação, logs, caches, credenciais e estado pessoal do editor.

[arquivos-somente-locais.json](arquivos-somente-locais.json) relaciona as referências omitidas, seus hashes originais e a justificativa. Os manifestos de CAD/PDF preservam o inventário da coleção local: **não são listas de arquivos necessariamente distribuídos pelo Git**. Links desses catálogos e notas para caminhos relacionados no inventário funcionam apenas na cópia local completa. Na cópia pública, consultar a URL de origem indicada no manifesto; não há download automático nem autorização implícita de redistribuição.

## Validação em uma cópia clonada

```bash
cd src/slamderson
uv run --no-project --with pytest==9.2.0 python -m pytest -p no:cacheprovider -q testes
```

Os testes conferem bytes e hashes de todas as referências presentes. Quando uma referência foi omitida do Git, exigem sua identificação exata no inventário de arquivos somente locais, com hash e justificativa. Uma ausência não declarada ou um arquivo presente adulterado continua sendo erro. O mesmo vale para links locais: somente alvos explicitamente inventariados podem estar ausentes da publicação.

Não existe licença geral escolhida para o projeto. Os avisos de terceiros continuam aplicáveis individualmente; uma licença geral não foi presumida durante a publicação.
