# Slamderson — documentação acadêmica

Esta pasta é a **fonte central da documentação do projeto**. Os textos são escritos em português brasileiro. A árvore `src/` contém código, metadados e recursos de execução, sem manuais distribuídos entre os módulos.

## Leitura recomendada

**Pesquisa e ideias:** [abrir o índice do vault Obsidian](vault-slamderson/Inicio.md). O [catálogo de fontes](vault-slamderson/05-fontes/Catalogo-de-fontes.md) reúne os originais disponíveis e as avaliações de confiabilidade.

**Modelos mecânicos:** [catálogo de modelos 3D](modelos-3d/catalogo.md), com arquivos de referência, licenças, prévias e validações. A correspondência às peças físicas ainda precisa ser conferida.

1. [Visão geral e situação do projeto](01-visao-geral.md).
2. [Arquitetura e fluxos de dados](02-arquitetura.md).
3. [Componentes, ligações e evidências](03-componentes-e-ligacoes.md).
4. [Comunicação UART](04-comunicacao-uart.md).
5. [Preparação do ambiente e desenvolvimento](05-desenvolvimento-e-execucao.md).
6. [Validação, ensaios e calibração](06-validacao-e-calibracao.md).
7. [Decisões e pendências](07-decisoes-e-pendencias.md).
8. [Responsabilidades das pastas](responsabilidades.md).
9. [Convenções de escrita e manutenção](convencoes.md).

## Publicação e referências locais

O repositório está destinado a <https://github.com/brenodelfinoligeiro/slam-mapeamento>. Consulte a [política de publicação](publicacao-git.md): alguns arquivos de referência são preservados apenas localmente por falta de autorização de redistribuição confirmada.

## Evidências e histórico

- [Histórico preservado](historico/LEIA-ME.md): documentação anterior, mantida como registro e não como instrução vigente.
- [Validação da centralização](validacao-centralizacao.md): resultados reais da reorganização e da revisão do acionamento.
- Acionamento atual: módulo L298N. Ligações funcionais e cuidados estão no [capítulo de componentes](03-componentes-e-ligacoes.md).

## Limite desta entrega

Existe uma estrutura de pacote ROS 2 `ament_python` no Xeon. Ainda não existem nós, controladores de dispositivos ou arquivos de inicialização implementados. A compilação do pacote não demonstra comunicação com o ESP, funcionamento do LiDAR, execução de SLAM ou movimento do robô.

A documentação deve evoluir com cada implementação. Informações desconhecidas permanecem marcadas como pendentes; resultados de ensaios não executados não devem ser apresentados como observados.
