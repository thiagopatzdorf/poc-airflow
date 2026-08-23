# Confiabilidade, retries e excecoes

## Politica de retries

| Classe | Exemplos | Comportamento |
|---|---|---|
| Transiente | timeout, HTTP 429/502/503, lock temporario | 2 tentativas (3 em fluxo critico), backoff exponencial de 30s ate 5min |
| Permanente | schema invalido, assinatura incorreta, regra violada | sem retry; quarentena e evento auditavel |
| Negocio | score alto, divergencia, documento pendente | nao e erro tecnico; segue para revisao humana |
| Desconhecida | excecao nao classificada | retries limitados, depois dead-letter + alerta |

Retries exigem operacao idempotente. Cada integracao futura deve aceitar uma chave composta
por `dag_id/run_id/task_id` ou verificar o estado antes de produzir efeitos. Nao se repete
automaticamente transferencia, bloqueio, notificacao externa ou outra acao irreversivel.

## Controles

- timeout de 5 minutos por task e apenas uma execucao ativa por DAG;
- concorrencia global limitada para proteger a honda;
- jitter deve ser aplicado em conectores externos futuros;
- dados invalidos seguem para `data/quarantine`, nunca sao descartados silenciosamente;
- depois do limite, o fluxo falha de forma visivel e exige decisao humana;
- reprocessamento preserva a referencia da execucao original;
- health checks cobrem API, scheduler e PostgreSQL.

## Recuperacao

1. Identificar se a falha e transiente, permanente ou de negocio.
2. Preservar logs e event hash; nunca editar evidencia no lugar.
3. Corrigir causa ou dado em uma nova versao/arquivo.
4. Reexecutar com justificativa e vinculo ao incidente.
5. Confirmar resultado e registrar fechamento.

