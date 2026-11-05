# Slamderson — área de trabalho ROS 2

Trabalho acadêmico de robótica móvel. Pacote `ament_python` localizado em `src/slamderson`, com módulos e documentação em português brasileiro. Nenhum dispositivo é aberto e nenhum motor é acionado por esta estrutura inicial.

## Uso

```bash
cd /home/lamggm/projects/slamderson_ws
uv venv .venv
uv pip install --python .venv/bin/python -r requisitos-desenvolvimento.txt
source .venv/bin/activate
colcon list
colcon build --packages-select slamderson
colcon test --packages-select slamderson
colcon test-result --verbose
source install/setup.bash
```

Em zsh, utilizar `source install/setup.zsh`. As dependências acima fornecem ferramentas de empacotamento e testes, não uma instalação completa do ROS 2.

## Validação e limites

A estrutura anterior foi compilada e testada com ferramentas isoladas em `/home/lamggm/.hermes/cache/scratch/slamderson-tools`. A localização para português foi compilada novamente e validada com **dois testes aprovados**; os detalhes estão em [validacao-localizacao.md](validacao-localizacao.md).

Não foi escolhido nem instalado um ROS 2 completo no Xeon nesta tarefa. A validação de empacotamento não equivale a executar nós ROS, comunicação DDS, sensores ou motores.

## Documentação

- [Apresentação do pacote](src/slamderson/LEIA-ME.md).
- [Responsabilidades](src/slamderson/documentacao/responsabilidades.md).
- [Convenções de português](src/slamderson/documentacao/convencoes.md).

O sufixo convencional `slamderson_ws` e os nomes de arquivos/chaves exigidos pelas ferramentas permanecem inalterados. Os diretórios próprios e os textos do projeto foram localizados. Não existe repositório Git inicializado nem licença selecionada nesta etapa.
