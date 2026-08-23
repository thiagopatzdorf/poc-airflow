# POC Airflow — Orquestração Cooperativa

> POC funcional, segura por padrão e auditável para demonstrar automações de uma cooperativa.

![Airflow](https://img.shields.io/badge/Apache_Airflow-3.3.1-017CEE?logo=apacheairflow)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)
![Security](https://img.shields.io/badge/dados-100%25_sint%C3%A9ticos-success)

## O que ela demonstra

Três DAGs transformam rotinas críticas em processos visíveis e rastreáveis:

| DAG | Fluxo | Controle-chave |
|---|---|---|
| `coop_transaction_monitoring` | monitoramento de transações | score explicável + revisão humana |
| `coop_kyc_onboarding` | onboarding/KYC | nenhuma aprovação quando há alerta |
| `coop_reconciliation` | conciliação | tolerância explícita + gate de integridade |
| `coop_agentic_reconciliation_hitl` | agentes + aprovação | contratos assinados, L1/L2 e dry-run |

Todos os dados são fictícios. A aplicação não se conecta a core bancário, não movimenta
valores e não toma decisão real sobre associados.

Além das DAGs demonstrativas, um [motor declarativo YAML](docs/DOCUMENT_WORKFLOWS.md) gera
fluxos de recebimento, leitura, envio, espera por N assinaturas e baixa de documentos.
As áreas validam a mesma definição por um [catálogo de fluxos](docs/FLOW_CATALOG.md)
gerado em linguagem de negócio.

## Arquitetura e segurança

- Airflow 3.3.1 oficial, Python 3.12, PostgreSQL 17 e `LocalExecutor`.
- Acesso apenas pelo IP Tailscale da `honda`; banco isolado na rede interna do Compose.
- Segredos únicos gerados localmente e nunca versionados.
- Containers sem privilégios adicionais e DAGs montadas como somente leitura.
- Eventos sem payload pessoal, identificadores pseudonimizados e cadeia SHA-256 verificável.
- Papéis separados para administrador, Segurança e Auditoria.

O fluxo agentico usa dois agentes determinísticos simulados para ser reproduzível e não
enviar dados para LLM externo. Eles apenas recomendam; política e duas pessoas distintas
controlam o avanço, e a ação final não produz efeito externo.

Veja [arquitetura](docs/ARCHITECTURE.md), [modelo de ameaças](docs/security/THREAT_MODEL.md)
e [checklist de Segurança](docs/security/SECURITY_CHECKLIST.md). A politica operacional de
[retries, idempotencia e recuperacao](docs/RELIABILITY.md) e unica para todas as DAGs.

## Subida rápida na honda

Pré-requisitos: Docker Engine com Compose v2 e acesso à tailnet.

```bash
make bootstrap
make init
make up
make status
```

Acesse `https://honda.tailf3785c.ts.net` pela tailnet. Na primeira inicialização, a senha do Simple Auth Manager é
gerada pelo Airflow em `config/simple_auth_manager_passwords.json.generated`. Trate o arquivo
como segredo, não o copie para tickets ou commits e troque o mecanismo por SSO/MFA antes de
qualquer ambiente real.

## Qualidade

```bash
make test
make lint
make security-check
```

O check local evita segredos triviais e valida a configuração, mas não substitui SAST,
scanner de imagens, pentest nem avaliação independente.

O GitHub executa uma esteira adicional com CodeQL, Bandit, Gitleaks, Trivy, dependency
review e SBOM. Veja as [evidencias e limites](docs/security/ASSESSMENT.md).

A [observabilidade](docs/OBSERVABILITY.md) inclui métricas nativas, Prometheus, dashboard
Grafana provisionado e regras para heartbeat e falhas, sem expor Prometheus no host.
Um [painel operacional para TV](docs/BUSINESS_TV.md) mostra filas, SLA, assinaturas
pendentes e conclusões por área.
O [modelo operacional](docs/OPERATING_MODEL.md) define personas de engenharia, ownership,
segregação de funções e o fluxo de mudança.
Responsabilidades, criação de DAGs e operação estão resumidas na [FAQ](docs/FAQ.md).
Toda automação segue um [fluxo de aprovação e promoção](docs/AUTOMATION_PROMOTION.md) antes
de ter seu schedule habilitado no Airflow.

## Operação

```bash
make status       # containers + health endpoint
make logs         # ultimas 200 linhas
make demo         # DAGs e caminho da interface
make down         # parada preservando o banco
```

Backups, restauração, atualização e resposta a incidentes devem seguir processos formais
antes de produção. O roteiro da apresentação está em [docs/DEMO.md](docs/DEMO.md).
O inventario e o unico passo privilegiado pendente da honda estao em
[docs/HONDA_DEPLOYMENT.md](docs/HONDA_DEPLOYMENT.md).

## Princípios

1. Humano continua responsável por decisões de impacto.
2. Regra determinística vence IA quando resolve o problema.
3. Cada execução deixa evidência verificável.
4. Menor privilégio e menor exposição desde o desenho.
5. POC é claramente separada de homologação e produção.

## Licença e uso

Uso interno para avaliação técnica. A inclusão de licença de distribuição depende de decisão
da cooperativa e dos responsáveis pelo repositório.
