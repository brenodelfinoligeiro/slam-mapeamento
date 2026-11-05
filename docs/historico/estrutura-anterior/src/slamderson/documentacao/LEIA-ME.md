# Arquitetura inicial

Consulte [responsabilidades.md](responsabilidades.md) para a divisão dos módulos e [convencoes.md](convencoes.md) para os critérios de idioma. As pastas separam responsabilidades; não representam obrigatoriamente processos ROS distintos.

Fluxo com o acionamento atual: `ROS 2/Raspberry <-> UART <-> ESP32 -> L298N -> motores`.
Os codificadores de rotação e a MPU-6050 são adquiridos pelo ESP e seus dados retornam na mesma UART. O LiDAR C1 fornece dados para percepção e mapeamento; ligação e controlador ainda precisam ser selecionados.

Divisão: dispositivos adquire e transmite; localização estima o estado; percepção processa dados; mapeamento constrói mapas; navegação planeja deslocamentos; controle trata os comandos. O PI das rodas permanece no ESP.

Identificadores convencionais como `cmd_vel`, `odom`, `imu/data_raw` e `scan` são propostas de interfaces ROS, não funcionalidades já implementadas. Eles não serão traduzidos de forma a quebrar a compatibilidade com os pacotes utilizados.

Escopo: protótipo didático e trabalho acadêmico. Não incorporar arquitetura industrial ou dependências de outro robô sem necessidade.
