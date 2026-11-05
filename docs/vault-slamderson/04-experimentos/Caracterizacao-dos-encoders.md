---
tipo: experimento
estado: proposto_nao_executado
atualizado: 2026-11-04
---
# Caracterização dos encoders

**Este é um procedimento proposto. Nenhuma tensão, contagem ou forma de onda abaixo representa resultado já medido.**

## Objetivo

Identificar revisão, alimentação, níveis de saída, resolução e comportamento dos módulos do carrinho sem transferir características de um produto parecido.

## Etapa 1 — inspeção desenergizada

- Fotografar ambas as faces, marcações do circuito integrado e nomes dos terminais.
- Verificar número de fios, correspondência entre terminais e existência de ajustes/indicadores.
- Identificar a saída mecânica medida e contar fendas como hipótese inicial de resolução.
- Se houver continuidade ou exame de resistores, fazer isso com o circuito desligado.

## Etapa 2 — sinal sem conexão ao GPIO

- Definir alimentação compatível com a placa identificada, usando fonte limitada.
- Medir alimentação e saída no estado livre e bloqueado do sensor.
- Registrar polaridade, nível alto/baixo e, quando possível, tempos de subida/descida no osciloscópio ou analisador apropriado.
- Confirmar compatibilidade com a entrada ESP antes de conectar. Não aplicar 12 V a partir da passagem contraditória do manual comparativo.

## Etapa 3 — resolução e velocidade

- Girar a roda por voltas completas conhecidas e contar eventos segundo uma convenção explícita.
- Repetir em cada roda e nos dois sentidos, sem afirmar que o canal único mede o sentido.
- Comparar resultado de borda única e ambas as bordas, se implementadas.
- Registrar C por volta da roda e calcular velocidade com a derivação de [[02-fundamentos/Contagem-e-odometria]].

## Etapa 4 — operação com o acionamento

- Iniciar com rodas suspensas e uma roda por vez.
- Observar pulsos extras, perda de eventos e influência da comutação do motor.
- Só dimensionar filtragem após observar o sinal; não copiar capacitor de outro módulo sem verificar perda de pulsos.
- Registrar também comando PWM e condições de alimentação, para distinguir falha óptica, ruído e falta de torque.

## Registro obrigatório

Data, identificador da roda/módulo, fotos, instrumentos, circuito realmente montado, versão do programa, alimentação, convenção de contagem, dados brutos e conclusão com limites. Usar [[07-modelos/Modelo-de-experimento]].

[[01-componentes/Encoder-MH-Sensor-Series]] · [[06-ideias/Ideias-e-pendencias]]
