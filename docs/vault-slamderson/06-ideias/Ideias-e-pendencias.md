---
tipo: ideias
estado: em_aberto
atualizado: 2026-11-04
---
# Ideias e pendências

## Resolver antes de fixar parâmetros

- Identificar o circuito integrado e a pinagem real dos módulos MH-Sensor-Series.
- Medir níveis de saída e eventos por volta da roda.
- Confirmar placa ESP e GPIOs disponíveis sem fechar a escolha por um periférico que não seja necessário.
- Identificar a placa L298N e verificar sua alimentação e jumpers.
- Medir partida, corrente e tensão útil nos motores TT.
- Identificar a placa adaptadora da MPU-6050 e a montagem dos eixos.
- Especificar aquisição, marcas temporais e contrato UART com dados reais.

## Possibilidades, não decisões

- Arranjo provisório em avaliação: pilhas AA para os motores informados pelo autor como 12 V e powerbank separado para a Raspberry Pi 5. Oito AA alcalinas em série dão 12 V nominais, mas não garantem corrente de partida adequada nem compensam a perda da L298N. Confirmar tensão no modelo real, química/número das AA, porta-pilhas, corrente de partida dos motores, saída USB-C real do powerbank, alimentação do ESP e forma de retenção física. Não dimensionar autonomia por mAh nominais sem conhecer conversão e carga.
- Para mockup mecânico, manter pack de pilhas baixo; usar cinta/suporte removível para powerbank e placas, com espaço para dissipador, conectores e fluxo de ar. Validar centro de massa e acesso antes de imprimir suportes definitivos.
- Comparar estimativa por janela e por intervalo de eventos quando a resolução for conhecida.
- Avaliar PCNT se a placa escolhida o disponibilizar; usar interrupções quando adequado ao volume real de pulsos.
- Investigar condicionamento ou filtragem se forem observados níveis incompatíveis ou pulsos falsos.
- Considerar codificadores em quadratura se a ambiguidade de sentido limitar os experimentos.

Não existem ganhos PI, taxa serial, frequência PWM ou covariâncias definidos por estas ideias. Registrar uma decisão somente depois de motivação e evidência.

[[03-decisoes/Arquitetura-atual]] · [[04-experimentos/Caracterizacao-dos-encoders]]
