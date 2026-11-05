# 5. Desenvolvimento e execução

## Caminhos e estrutura

Raiz da área de trabalho: `/home/lamggm/projects/slamderson_ws`.

- `docs/`: documentação acadêmica, procedimentos, decisões e evidências.
- `src/slamderson/`: pacote ROS 2, testes e recursos de execução.
- `requisitos-desenvolvimento.txt`: versões das ferramentas utilizadas no empacotamento.
- `build/`, `install/` e `log/`: resultados gerados pelo colcon, não fontes de documentação.

O nome `docs/` foi mantido por solicitação explícita do autor. Seu conteúdo é em português. Os demais diretórios próprios permanecem localizados.

## Preparação isolada das ferramentas

```bash
cd /home/lamggm/projects/slamderson_ws
uv venv .venv
uv pip install --python .venv/bin/python -r requisitos-desenvolvimento.txt
source .venv/bin/activate
```

Isso prepara ferramentas de empacotamento e teste. Não instala uma distribuição ROS 2 completa. A validação anterior utilizou um ambiente temporário em `/home/lamggm/.hermes/cache/scratch/slamderson-tools`; não depender desse cache como instalação permanente.

## Compilação e testes

```bash
colcon list
colcon build --packages-select slamderson
colcon test --packages-select slamderson
colcon test-result --verbose
source install/setup.bash
```

Em zsh, usar `source install/setup.zsh`. O pacote deve ser reconhecido como `ros.ament_python`. Os testes usam arquivos `testes/teste_*.py` e funções `teste_*`, configurados em `setup.cfg`.

Após mudanças na organização, verificar importações a partir de `install/` fora da pasta fonte. Conferir também a ausência de módulos antigos que possam permanecer em instalações incrementais.

## Instalação dos recursos

`setup.py` instala o manifesto, o marcador ament e os recursos das pastas `inicializacao`, `configuracao`, `descricao`, `mapas` e `visualizacao`. Na ausência de arquivos reais, essas pastas contêm apenas marcadores vazios `.gitkeep`.

A documentação de `docs/` não faz parte dos módulos Python nem é instalada como recurso de execução. Não acrescentar cópias de manuais aos diretórios de código para que apareçam no pacote.

## Execução futura

Ainda não existem executáveis registrados ou arquivos de inicialização. Comandos como `ros2 run` e `ros2 launch` não iniciarão funcionalidades próprias nesta etapa. Para validar nós, comunicação DDS e sensores será necessário selecionar e preparar uma distribuição ROS 2 compatível com o alvo.

Não foram assumidos portas de dispositivos, taxa serial, versão de controlador C1 ou acesso remoto à Raspberry. Essas informações serão registradas quando forem medidas ou configuradas.

## Metadados

Nome do pacote: `slamderson`. A licença e o contato de manutenção continuam pendentes; `a_definir@example.com` é apenas um endereço ilustrativo. Não atribuir licença ou autoria institucional sem decisão do autor.
