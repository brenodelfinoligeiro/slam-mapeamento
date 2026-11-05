# Convenções de idioma e documentação

## Regra central

**Toda documentação detalhada do projeto fica em `docs/`, na raiz da área de trabalho e fora de `src/`.** A organização foi solicitada para manter o código separado de relatórios, decisões, tutoriais e justificativas acadêmicas.

- Não distribuir arquivos de apresentação entre módulos, testes e recursos de execução.
- Não instalar manuais como parte dos módulos Python ou como dados necessários à execução.
- Não usar arquivos `__init__.py` para registrar arquitetura ou histórico. Nesta etapa eles apenas estabelecem os pacotes e podem permanecer vazios.
- Comentários locais úteis e documentação curta de uma interface podem acompanhar o código; não substituir um manual por comentários extensos.
- Manter o índice atualizado quando houver novo capítulo.
- A exceção operacional é `AGENTS.md`, na raiz, solicitado pelo autor para orientar os agentes a manterem `docs/vault-slamderson/`. Ele não substitui nem recebe a documentação técnica detalhada.

## Vault de pesquisa

Organizar fontes, PDFs, ideias, decisões e experimentos em [vault-slamderson/Inicio.md](vault-slamderson/Inicio.md). Atualizar as notas e os capítulos-resumo na mesma entrega quando uma mudança relevante alterar o conhecimento do projeto. Preservar a distinção entre fonte primária, módulo semelhante, oferta comercial e medição real.

## Português brasileiro

Usar português nos nomes próprios de pastas, variáveis, funções, mensagens, comentários e textos. Identificadores de código e pastas não usam acentos; documentos UTF-8 mantêm acentuação normal. Adotar redação técnica apropriada ao trabalho acadêmico.

A pasta `docs/` é uma exceção de nomenclatura solicitada explicitamente pelo autor. Seu conteúdo permanece em português. O nome `slamderson` e a raiz `slamderson_ws` também são preservados.

## Compatibilidade com ferramentas

Não traduzir nomes exigidos pelas ferramentas, como `package.xml`, `setup.py`, `setup.cfg`, `__init__.py`, `.gitignore`, chaves de configuração, nomes de dependências e diretórios gerados por colcon. O índice ament mantém seu caminho padronizado mesmo que a pasta fonte se chame `recursos`.

Tipos de mensagem e interfaces de pacotes externos, como `sensor_msgs/Imu`, `sensor_msgs/LaserScan`, `cmd_vel`, `odom` e `base_link`, não devem ser traduzidos de modo a quebrar contratos. Interfaces próprias futuras devem ser nomeadas em português quando isso não prejudicar a integração.

Os testes são coletados em `testes/teste_*.py`, com funções `teste_*`.

## Qualidade da evidência

Distinguir explicitamente: informação fornecida pelo autor, observação visual, hipótese, recomendação de projeto e resultado real. Registrar uma pendência em vez de inventar pino, taxa, ganho, dimensão ou medição.

Uma validação deve indicar comando/procedimento, ambiente e resultado. Procedimentos futuros ficam separados de ensaios executados. Dados acadêmicos não devem ser preenchidos com resultados sintéticos apresentados como medições reais.

## Histórico

A documentação substituída pode ser preservada em `docs/historico/` com indicação clara de que não é a referência vigente. Não reintroduzir sua organização antiga na árvore fonte.
