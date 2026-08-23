# Fluxo de aprovacao — da ideia ao Airflow

1. PROPOSTA: problema, dono, beneficio, volume, frequencia e SLA.
2. TRIAGEM: classificar dados, efeito e reversibilidade.
3. CONTRATO: schema, fonte oficial, estados, idempotencia, retries e timeout.
4. IMPLEMENTACAO: YAML para capacidade existente; Python testado para capacidade nova.
5. GATES: testes, schema, SAST, secrets, IaC/container scan e SBOM.
6. AREA: validar regra, SLA, catalogo, painel e criterio de aceite.
7. REVISAO: Plataforma, Integracoes, Seguranca e Auditoria conforme risco.
8. HOMOLOGACAO: casos normal, limite, falha, timeout, duplicidade e rollback sinteticos.
9. DEPLOY PAUSADO: codigo presente, mas automacao ainda nao autorizada.
10. EXECUCAO OBSERVADA: disparo manual e evidencia ponta a ponta.
11. HABILITACAO: schedule liberado, janela de observacao e criterio de rollback.

## Reviews por risco

| Risco | Reviews minimos |
|---|---|
| Baixo | Automacao da area + Plataforma |
| Medio | Automacao da area + Integracoes + Seguranca |
| Alto | Dono formal + Plataforma + Seguranca + Auditoria; four-eyes |

Risco alto nao recebe efeito automatico nesta POC.

## Regras

- Autor nao e o unico aprovador.
- Gate vermelho impede merge; excecao tem dono, justificativa e prazo.
- YAML nunca recebe shell, segredo, SQL livre, URL arbitraria ou codigo.
- A DAG entra pausada; deploy nao significa autorizacao para agendar.
- Mudanca emergencial expira e exige revisao posterior.
- Falha na janela inicial pausa e reverte; nao se ajusta direto em producao.

