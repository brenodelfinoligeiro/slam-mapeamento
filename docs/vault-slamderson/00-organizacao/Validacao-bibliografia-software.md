---
tipo: validacao
atualizado: 2026-11-07
estado: verificado_com_ressalva_na_suite_global
---
# Auditoria da bibliografia de software

## Escopo

Pesquisa ligada em [[05-fontes/Software-e-monografia]], com fichas, trechos, URLs, BibTeX e originais efetivamente obtidos. A auditoria confere integridade documental e referências internas; não executa ROS, simulador ou hardware e não certifica a formatação final da monografia.

## Resultado

- **14 fontes de software verificadas:** seis trabalhos científicos e oito documentos oficiais/de mantenedores, com identificadores estáveis 24–37.
- **15 documentos novos com citações** aprovados em `sources.py verify --evidence`; o catálogo preexistente também passou. O teste confere IDs, endereços e presença de trechos, não substitui avaliação científica.
- **329 vínculos locais do vault** conferidos, juntamente com âncoras no código, trechos e hashes das evidências, metadados e PDFs. O nome privado está ausente dos 15 textos novos de pesquisa; caminhos legados foram preservados.
- **BibTeX analisado com bibtexparser 2.1.0:** 33 entradas no arquivo único, incluindo 14 novas, sem blocos de falha ou chaves duplicadas. Isso valida leitura sintática, não regras ABNT da instituição.
- **Dois PDFs integrais novos:** JOSS/SLAM Toolbox, 7 páginas; revisão SLAM 2D de 2025, 28 páginas. Cabeçalhos, `pdfinfo` e SHA-256 conferidos; incluídos no manifesto e no inventário de cópias somente locais.

A suíte estrutural existente foi executada na **árvore compartilhada completa**: **17 aprovados e uma falha**. O teste de links interpreta a lista de pontos x,y entre colchetes duplos, escrita como código inline em `docs/web/contrato-implementacao.md`, como um wikilink para `docs/x,y.md`. Esse documento é trabalho concorrente, fora desta pesquisa, e não foi modificado. A auditoria específica do vault passou; **não houve aprovação global da árvore**.

Recibo estruturado: `05-fontes/software-validacao.json`. O acesso MDPI HTML falhou, mas o PDF editorial oficial foi recuperado. RPP e Moore–Stouch foram usados a partir de resumo/metadados, sem alegação de leitura integral. Não foram executados novos ensaios ROS, simulador ou hardware.

## Procedimento

A partir da raiz do vault: `python 05-fontes/validar-software.py`. O verificador confere IDs, trechos literais, hashes, vínculos, âncoras locais e entradas BibTeX. Os documentos com citações também são conferidos com `sources.py verify --evidence` da ferramenta de referências usada na coleta.

O conjunto estrutural existente do pacote de descrição é executado separadamente sobre a cópia local completa. Aprovação documental não é novo ensaio de navegação.

[[Inicio]] · [[05-fontes/Catalogo-de-fontes]]
