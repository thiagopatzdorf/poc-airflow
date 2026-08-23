# Modelo de ameacas (STRIDE resumido)

| Ameaca | Controle da POC | Lacuna para producao |
|---|---|---|
| Falsificacao de identidade | Tailscale + autenticacao Airflow + usuarios por papel | Integrar IdP/MFA corporativo |
| Adulteracao | DAGs read-only, Git, auditoria encadeada por hash | WORM/SIEM externo e assinatura assimetrica |
| Repudio | timestamps UTC, actor do Airflow, logs e event hashes | carimbo de tempo confiavel externo |
| Vazamento | dados sinteticos, secrets fora do Git, banco sem porta | KMS/Vault, DLP e classificacao institucional |
| Negacao de servico | limites de concorrencia, health checks, restart | HA, quotas e plano formal de DR |
| Elevacao de privilegio | cap-drop, no-new-privileges, rede interna | rootless containers e hardening CIS do host |

## Fronteiras de confianca

1. Dispositivo autorizado entra na tailnet.
2. Airflow autentica o usuario e aplica o papel.
3. Scheduler executa apenas DAG versionada e montada como somente leitura.
4. Tasks escrevem somente em areas de dados/logs designadas.

## Premissas

- A tailnet e as identidades dos dispositivos sao administradas corretamente.
- Somente mantenedores autorizados possuem SSH na honda.
- Nenhum dado real deve ser introduzido na POC.

