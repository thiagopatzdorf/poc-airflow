# Observabilidade

## Stack

```text
Airflow --StatsD/UDP--> statsd-exporter <--scrape-- Prometheus <--query-- Grafana
```

- StatsD exporter converte metricas nativas do Airflow para Prometheus.
- Prometheus retém no máximo 15 dias ou 2 GB e não publica porta no host.
- Grafana é provisionado por código, sem cadastro aberto ou acesso anônimo.
- Dashboard mostra disponibilidade, heartbeat, sucesso/falha e resultado por DAG/task.
- Regras detectam ausência de métricas, scheduler sem heartbeat e falhas recentes.

## Acesso

Grafana escuta apenas em `127.0.0.1:3000`. Depois de habilitar Tailscale Serve:

```bash
tailscale serve --bg --https=8443 http://127.0.0.1:3000
```

URL: `https://honda.tailf3785c.ts.net:8443`.

O [painel de negócio em modo TV](BUSINESS_TV.md) usa um process store separado e apresenta
SLA, filas e assinaturas sem expor detalhes técnicos das DAGs.

## Logs e auditoria

- Logs técnicos permanecem no Airflow e não devem conter payload documental.
- Eventos de negócio usam referências pseudonimizadas, UTC, resultado e HMAC encadeado.
- Logs Airflow e a cadeia local não substituem SIEM/WORM. Produção exige exportação
  off-host, retenção institucional, controle de acesso e teste de restauração.

## Alertas

As regras estão implementadas e visíveis no Prometheus/Grafana, mas não há canal de
notificação configurado na POC. Alertmanager/e-mail/Teams/PagerDuty dependem de destino e
credencial fornecidos pela cooperativa; falha de alerta não deve ser escondida.
