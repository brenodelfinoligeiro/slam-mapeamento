---
tipo: fundamento
estado: derivacao_teorica_nao_ensaio
atualizado: 2026-11-04
---
# Contagem de pulsos e odometria

## Definir a resolução primeiro

Defina C como o número de **eventos efetivamente contados por volta da roda**. C depende do disco, da posição de montagem e da borda contada. Contar somente subida e contar ambas as bordas são convenções diferentes; o número de fendas não pode ser copiado automaticamente para C.

Se o sensor medir um eixo antes de uma redução, a transmissão deve ser considerada. No conjunto observado, o disco está na outra ponta da mesma saída mecânica que move a roda; confirmar a montagem durante o ensaio.

## Derivação da velocidade

Para uma janela de duração Δt, com ΔN eventos contados:

$$f = \frac{\Delta N}{\Delta t}, \qquad \mathrm{RPM} = \frac{60\,\Delta N}{C\,\Delta t} = \frac{60 f}{C}.$$

A velocidade angular da roda é:

$$\omega = \frac{2\pi\,\Delta N}{C\,\Delta t}.$$

Para medir o intervalo T entre eventos consecutivos igualmente espaçados, a relação é RPM = 60/(C T). Essas expressões são derivações por contagem de eventos e conversão de unidades; não são resultados experimentais.

## Exemplo idealizado verificado em Python

Com um evento contado por volta e intervalo de três segundos, RPM = 20. Com dois eventos por volta e o mesmo intervalo entre eventos, RPM = 10. O cálculo executado foi `60 / (eventos_por_volta * intervalo_s)`.

O manual WPSE347 dá 180 e 90 RPM nesses exemplos, respectivamente. O erro e as inconsistências do documento estão registrados em [[05-fontes/notas/Fonte-02-Whadda-WPSE347]]. Não reproduzir a fórmula publicada como referência correta.[2]

## Distância e cinemática diferencial

Se R for o raio efetivo da roda, o deslocamento associado a uma contagem com sinal confiável é:

$$\Delta s = \frac{2\pi R\,\Delta N}{C}.$$

Com velocidades tangenciais vE/vD e distância b entre rodas, sob hipótese de rolamento sem deslizamento:

$$v = \frac{v_D+v_E}{2}, \qquad \dot{θ} = \frac{v_D-v_E}{b}.$$

As expressões decorrem da geometria do modelo idealizado. Não estabelecem precisão real nem substituem medição de geometria e comparação com referência externa.

## Ambiguidade de sentido

Um único canal fornece contagens, mas não uma sequência de quadratura que determine o sentido. Usar o comando da L298N como sinal é uma hipótese de operação, não uma medição independente. Embalo, deslocamento externo e patinagem precisam ser considerados. A IMU ajuda a avaliar coerência do giro do chassi, mas não resolve toda ambiguidade de translação.

[[01-componentes/Encoder-MH-Sensor-Series]] · [[04-experimentos/Caracterizacao-dos-encoders]]

## Sources

[2] https://cdn.velleman.eu/downloads/25/wpse347a4v01.pdf — Velleman — WPSE347: IR speed sensor module
