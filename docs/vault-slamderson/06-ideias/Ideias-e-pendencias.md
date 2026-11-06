---
tipo: ideias
estado: em_aberto
atualizado: 2026-11-04
---
# Ideias e pendências

## Resolver antes de fixar parâmetros

- O [[01-componentes/Powerbank-Basike|Basike real]] de 150 × 70 × 30 mm e 420 g indicados já está corrigido na [R02](../../carcaca-r02/LEIA-ME.md), em berço traseiro baixo. Validar retenção, cabos, estabilidade, térmica com carcaça fechada e fornecimento real de 5 V/3 A à Pi. A geometria foi atualizada; os ensaios físicos continuam pendentes.

- Identificar o circuito integrado e a pinagem real dos módulos MH-Sensor-Series.
- Medir níveis de saída e eventos por volta da roda.
- Confirmar placa ESP e GPIOs disponíveis sem fechar a escolha por um periférico que não seja necessário.
- Identificar a placa L298N e verificar sua alimentação e jumpers.
- Medir partida, corrente e tensão útil nos motores TT.
- Identificar a placa adaptadora da MPU-6050 e a montagem dos eixos.
- Especificar aquisição, marcas temporais e contrato UART com dados reais.

## Possibilidades, não decisões

- O autor fechou quatro AA. O [estudo de disposição 2D](../../disposicao-2d/LEIA-ME.md) propõe dois pisos e ponte para o C1, com reservas explícitas de holder, ESP e powerbank. A quantidade não é hipótese; química, suporte exato, posições e fixações continuam em aberto. Quatro alcalinas fornecem 6 V nominais antes das perdas na L298N, insuficientes para presumir desempenho nominal de motores informados como 12 V. Validar partida, corrente, torque, refrigeração e saída real do powerbank; não presumir autonomia por mAh nem acrescentar conversor elevador sem decisão.
- Para mockup mecânico, manter pack de pilhas baixo; usar cinta/suporte removível para powerbank e placas, com espaço para dissipador, conectores e fluxo de ar. Validar centro de massa e acesso antes de imprimir suportes definitivos.
- [Estudo 3D](../../montagem-3d/LEIA-ME.md) gerado a partir dos CADs locais: ESP e L298N elevados em 6 mm em relação ao 2D para liberar os suportes dos motores no CAD original. Discos, fixações, holder, ESP e powerbank permanecem ilustrativos/propostos; não assumir alinhamento óptico, resolução dos discos, ausência de colisões ou estabilidade física.
- Comparar estimativa por janela e por intervalo de eventos quando a resolução for conhecida.
- Avaliar PCNT se a placa escolhida o disponibilizar; usar interrupções quando adequado ao volume real de pulsos.
- Investigar condicionamento ou filtragem se forem observados níveis incompatíveis ou pulsos falsos.
- Considerar codificadores em quadratura se a ambiguidade de sentido limitar os experimentos.

Não existem ganhos PI, taxa serial, frequência PWM ou covariâncias definidos por estas ideias. Registrar uma decisão somente depois de motivação e evidência.

[[03-decisoes/Arquitetura-atual]] · [[04-experimentos/Caracterizacao-dos-encoders]]
