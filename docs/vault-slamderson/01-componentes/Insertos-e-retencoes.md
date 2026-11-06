# Fixação com insertos — requisitos R05

O autor determinou reutilizar os insertos M3 da tampa traseira do motor Kalatec, eliminar porcas e não usar velcro ou cintas plásticas no Slamderson.

## Medidas recuperadas

- Rosca M3.
- Diâmetro liso informado: 4,0 mm.
- Diâmetro sobre os dentes: 4,7 mm.
- Comprimento corrigido pelo autor: **5,68 mm**, substituindo os 10,7 mm iniciais.

[Parâmetros e trechos de evidência](../../fixacao-r05/requisitos-insertos.json) identificam a conversa, datas e linhas das mensagens, sem copiar o histórico integral ou dados de conexão. A mensagem posterior confirma os demais diâmetros. Espessuras e apoios pedidos para a tampa do motor não são automaticamente requisitos do carrinho.

## Restrições e pendência de projeto

As retenções de Basike e ESP devem ser rígidas e removíveis por parafusos, sem velcro/faixas/abraçadeiras plásticas. O berço não deve exercer pressão pontual sobre o powerbank. A forma e as folgas ainda precisam de revisão CAD.

Os furos da Pi no CAD são de 2,7 mm: não alargar PCB nem presumir que M3 passe. O autor confirmou **presilhas rígidas pelas bordas, aparafusadas nos mesmos insertos M3**, sem alargar os furos dos PCBs. Não introduzir insertos menores nem usar M3 forçado nos furos da Pi. A instalação térmica dos insertos exige acesso, material ao redor e ensaio do alojamento, não apenas trocar o bolso sextavado por um cilindro.

**Estado:** [CAD/STL R05](../../fixacao-r05/LEIA-ME.md) gerados e auditados digitalmente; 29 modelos (28 de montagem + cupom), 44 impressos de montagem, 68 insertos M3 e 68 parafusos, sem porcas/velcro/cintas. Fatiamento Orca dos 29 modelos concluído, sem impressão. Cupom primeiro; chassi/C1/ESP/holder reais ainda pendentes. R04 e seu manual continuam históricos e não atendem às novas restrições.

[[03-decisoes/Arquitetura-atual]] · [[01-componentes/Powerbank-Basike]]
