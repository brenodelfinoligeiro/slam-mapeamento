# Validação da centralização da documentação

## Escopo

Comprovar a separação entre a documentação acadêmica, localizada em `docs/`, e o código, os metadados e os recursos instalados do pacote. O cache de teste é direcionado a `build/` para não depositar Markdown em `src/`.

## Verificações realizadas

Os resultados de compilação e instalação abaixo pertencem à etapa de centralização. A revisão documental para L298N é registrada separadamente na seção seguinte.

- `python -m pytest -q`, executado na pasta do pacote: 3 testes passaram.
- `colcon build --packages-select slamderson`: código de saída zero.
- `colcon test --packages-select slamderson`: código de saída zero.
- `colcon test-result --verbose`: 3 testes, 0 erros, 0 falhas, 0 ignorados.
- Importação do pacote instalado e de nove módulos estruturais: passou.
- Pacote visível no índice ament e cinco pastas de recursos instaladas: verificado.
- Documentação `.md` fora de `docs/`, desconsiderados artefatos e ambientes gerados: nenhuma.
- Documentação Markdown no pacote instalado: nenhuma.
- Os anexos de acionamento anteriores foram retirados desta edição e preservados fora da área de trabalho, junto à cópia de segurança anterior à adoção da L298N.
- Vínculos relativos e conteúdo de acionamento foram verificados novamente na revisão documental para L298N, descrita a seguir.

## Revisão documental para L298N

Em 4 de novembro de 2026, o acionamento foi atualizado para módulo L298N, incluindo visão geral, arquitetura, ligações funcionais, responsabilidades, ensaios e pendências. Os documentos históricos também foram ajustados quanto ao acionamento, sem apresentá-los como cópias intocadas.

- Testes Python de estrutura, localização e separação documental: 3 passaram, sem falhas.
- Auditoria dos 32 documentos Markdown: 27 vínculos relativos, nenhum destino ausente.
- Busca pelos identificadores do acionamento anterior, nomes de componentes e formatos de projeto retirados: nenhuma ocorrência nos arquivos ou nomes de arquivos em `docs/`.
- Sete arquivos anexos anteriores retirados dos documentos e conferidos por SHA-256 contra a cópia de segurança.
- Nenhum código de controle ou configuração de hardware foi alterado nesta revisão.

O ambiente temporário colcon da validação anterior não estava mais disponível. Não foi realizado novo build colcon nesta revisão exclusivamente documental. Os testes foram executados em ambiente isolado com o comando abaixo, na pasta `src/slamderson/`:

```bash
uv run --no-project --with pytest==9.2.0 python -m pytest -c setup.cfg -o cache_dir=/home/lamggm/.hermes/cache/scratch/slamderson-l298n-pytest -q testes
```

## Ambiente e limites

A validação foi realizada no Xeon com ferramentas colcon/teste isoladas em `/home/lamggm/.hermes/cache/scratch/slamderson-tools`. Não comprova uma distribuição ROS 2 instalada, execução de nós, integração de hardware, UART, condução de motores, localização, SLAM ou navegação.

O acionamento atual será feito por módulo L298N. A documentação registra ligações funcionais, mas não confirma GPIOs físicos, alimentação ou jumpers de uma placa específica. Não foi realizado ensaio elétrico ou de movimento com esse módulo.

## Relatórios e preservação

Logs do build e dos testes da centralização foram preservados em `/home/lamggm/.hermes/backups/slamderson/2026-11-04_085943/validacao/`. A cópia integral anterior à centralização está em `/home/lamggm/.hermes/backups/slamderson/2026-11-04_085943/antes-da-centralizacao.tar.gz`.

A documentação anterior à adoção da L298N foi preservada em `/home/lamggm/.hermes/backups/slamderson/2026-11-04_143718-l298n/documentacao-anterior.tar.gz`. Os anexos retirados estão na pasta `anexos-retirados/` dessa mesma cópia de segurança, fora do projeto. Os documentos históricos disponíveis em `docs/` foram ajustados quanto ao acionamento para não orientar uma montagem obsoleta.
