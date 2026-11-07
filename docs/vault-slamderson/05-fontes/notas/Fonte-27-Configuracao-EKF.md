---
tipo: fonte
estado: texto_primario_consultado
acesso: 2026-11-07
fonte_id: 27
---
# robot_localization — Configuring robot_localization (branch ros2)

## Identificação

- Tipo: especificação oficial/convenção ROS ou documentação dos mantenedores, não artigo revisado por pares.
- Data de publicação: s.d.; documentação viva consultada em 2026-11-07, não artigo publicado em 2026.
- Versão/recorte: branch ros2; não tag Jazzy fixa.
- URL consultada: <https://raw.githubusercontent.com/cra-ros-pkg/robot_localization/ros2/doc/configuring_robot_localization.rst>.
- URL efetiva: <https://raw.githubusercontent.com/cra-ros-pkg/robot_localization/ros2/doc/configuring_robot_localization.rst>.
- Acesso: 2026-11-07T09:29:57.590395-03:00.

## Evidência e avaliação

> If so, please set the ``two_d_mode`` parameter to *true*. This effectively zeros out the 3D pose variables in every measurement and forces them to be fused in the state estimate.

O parâmetro `two_d_mode` restringe o estado ao caso planar.[27]

Seção verificável: procurar o trecho acima no texto preservado. A página não é paginada; não há número de página inventado.

## Aplicação na monografia

Explicar rodas + velocidade angular Z, evitando duplicar pose de rodas e velocidade correlacionadas. Não atribuir orientação absoluta observada à MPU-6050.

**Evidência local inspecionada:** `src/localizacao/fusao_sensores/configuracao/estimador.yaml`, relativa à raiz do workspace. A fonte externa explica o método/interface; a configuração local informa a escolha efetiva. Os resultados são os recibos do projeto, não o desempenho publicado por terceiros.

## Preservação e limites

Texto recuperado por HTTP e extraído sem scripts: [evidência local](../evidencias/software-27.txt). SHA-256 do UTF-8 extraído: `ce1e3912b44721b701b259e751215dc67f6a77192373f4e3f885406eac9dd433`. Não é PDF, cópia integral do HTML nem snapshot imutável do repositório. Branches/portais podem mudar; a coleta datada e o hash delimitam o texto consultado. Cópia integral mantida somente localmente pela política de publicação.

## Relações

[[05-fontes/Software-e-monografia]] · [[04-experimentos/Simulacao-odometria-IMU-teleop]] · [[00-organizacao/Criterios-de-confiabilidade]]

## Sources

[27] https://raw.githubusercontent.com/cra-ros-pkg/robot_localization/ros2/doc/configuring_robot_localization.rst — robot_localization — Configuring robot_localization (branch ros2)
