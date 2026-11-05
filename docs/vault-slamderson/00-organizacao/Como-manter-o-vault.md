---
tipo: procedimento
atualizado: 2026-11-04
---
# Como manter o vault

## A cada mudança relevante

1. Ler [[Inicio]] e a nota do componente envolvido.
2. Registrar a nova fonte no catálogo; preservar autoria, título, revisão, data de acesso, endereço consultado e aplicabilidade.
3. Baixar o original quando disponível; conferir se é realmente PDF, se abre e se contém o documento esperado. Não converter HTML em PDF e apresentá-lo como datasheet original.
4. Associar ao PDF seu SHA-256 e número de páginas em `05-fontes/manifesto-arquivos.json`. Registrar o hospedeiro quando diferente do autor.
5. Colocar as afirmações técnicas com referências numeradas ao lado e indicar a página/seção relevante. Registrar trechos verificáveis, sem parafraseá-los como se fossem citações literais.
6. Atualizar a nota do componente, os fundamentos ou a decisão afetada. Vincular notas relacionadas com wikilinks.
7. Se houver medição, registrar instrumento, configuração, programa, alimentação, arquivos brutos e limites; separar procedimento proposto de resultado executado.
8. Atualizar o capítulo-resumo correspondente em `docs/` e o índice quando necessário.
9. Verificar links, hashes e testes. Não declarar como realizado um ensaio que só foi planejado.

## Referências locais

O registro `citacoes.json` mantém os identificadores das fontes e citações literais. Não renumerar referências existentes. Os registros de coleta preservam também os acessos que falharam; um endereço descoberto na busca não significa que seu conteúdo foi lido.

O cabeçalho `Sources` ao final de notas técnicas é gerado pela ferramenta de referências; mantém-se esse nome técnico para a validação automática. As notas autorais e instruções são escritas em português; documentos e citações dos fabricantes permanecem no idioma original.

## Organização

- `01-componentes/`: síntese por equipamento e limitações de identificação.
- `02-fundamentos/`: conceitos, derivações e hipóteses de validade.
- `03-decisoes/`: escolhas efetivamente feitas e suas razões.
- `04-experimentos/`: procedimentos e registros de ensaios.
- `05-fontes/`: catálogo, originais, textos extraídos, evidências e manifestos.
- `06-ideias/`: possibilidades ainda não decididas.
- `07-modelos/`: modelos para novas notas.

Usar [[07-modelos/Modelo-de-fonte]] e [[07-modelos/Modelo-de-experimento]]. Não modificar PDFs de terceiros nem remover avisos de autoria. Os estados de janelas do Obsidian não são evidência de pesquisa.
