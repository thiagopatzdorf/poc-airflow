# Modelo operacional — engenharia de software com enfase em automacao

Todas as personas trabalham como engenheiros de software. O que muda e o dominio, a
autoridade e o tipo de evidencia pelo qual respondem.

| Persona | Responsabilidade | Pode mudar | Nao pode aprovar sozinho |
|---|---|---|---|
| `area_automation_engineer` | fluxo, regra, SLA e indicador da area | YAML e testes do proprio fluxo via PR | mudanca propria de alto impacto |
| `integration_data_engineer` | eventos, schemas, idempotencia e qualidade | conectores e contratos versionados | excecao de negocio |
| `orchestration_platform_engineer` | Airflow, deploy, capacidade, backup e observabilidade | plataforma e runtime via PR | regra da area ou acesso proprio |
| `security_automation_engineer` | IAM, threat model, scans e evidencias | policies e gates de seguranca | excecao que reduza seu proprio controle |
| `human_decision_engineer` | investigar e decidir casos HITL | decisao vinculada ao caso/payload | caso criado ou alterado pela mesma identidade |
| `audit_reliability_engineer` | reconstruir execucao e testar controles | consultas e relatorios read-only | executar, reprocessar ou editar evidencia |

## Ownership por fluxo

Cada YAML declara area de negocio, engenheiro dono da automacao, engenheiro de plataforma,
engenheiro de seguranca, dono das excecoes, SLA, entradas, saidas e signatarios. Esses
campos aparecem no catalogo e no painel da TV.

## Fluxo de mudanca

```text
hipotese da area
  → PR do area_automation_engineer
  → testes deterministas
  → revisao integration/platform quando aplicavel
  → security gate
  → aprovacao por identidade diferente
  → deploy gradual
  → metricas + periodo de observacao
  → promover ou reverter
```

Mudanca de YAML e mudanca de software: passa por versionamento, review, teste, evidencia e
rollback. Incidente gera detector, teste ou runbook para que o mesmo erro nao dependa
novamente de memoria humana.

## Segregacao minima

- autor de mudanca nao e seu unico aprovador;
- operador de plataforma nao edita evidencia;
- aprovador de caso nao altera regra durante a decisao;
- auditor nao possui credencial de execucao;
- acesso emergencial expira, exige justificativa e revisao posterior.

