# FAQ — Orquestracao e automacoes

## Quem mexe no Airflow?

O `orchestration_platform_engineer`. Essa persona instala, atualiza e opera Airflow,
PostgreSQL, Prometheus e Grafana; cuida de disponibilidade, capacidade, backup, secrets,
deploy, rollback e incidentes da plataforma. Mudancas passam por PR e revisao.

## Quem constroi as DAGs?

Existem duas camadas:

1. O `orchestration_platform_engineer` constroi a factory de DAGs, operators, sensores,
   callbacks, retries e controles reutilizaveis.
2. O `area_automation_engineer` cria ou altera fluxos normais preenchendo YAML validado:
   objetivo, area, SLA, entradas, saidas, signatarios, prazos e tratamento de excecao.

Python muda quando nasce uma nova capacidade. YAML muda quando uma area cria uma variacao
de processo usando capacidades existentes.

## A area de negocio precisa saber Python?

Nao para criar uma variacao suportada. Ela revisa o catalogo gerado, valida o fluxo e pode
alterar YAML via PR assistido. Como todos atuam com mentalidade de engenharia, a mudanca
continua versionada, testada, revisada e reversivel.

## Quem cria conectores com GED, assinatura, e-mail ou core?

O `integration_data_engineer`, em conjunto com o dono da automacao. O conector deve ter
contrato versionado, idempotency key, timeout, retry apenas para falhas transientes,
reconciliacao e testes de contrato. Credenciais ficam fora do YAML e do Git.

## Quem define a regra do processo?

O `area_automation_engineer` responde pela regra e pelo indicador, com aprovacao do dono
formal da area. Plataforma implementa o mecanismo, mas nao inventa regra de negocio.

## Quem decide uma excecao?

O `human_decision_engineer` designado para aquele tipo de caso. Alto risco exige duas
identidades distintas. A pessoa que criou ou mudou o caso nao pode ser sua unica aprovadora.

## Quem pode alterar retries e timeouts?

A politica global e mantida por Plataforma/SRE. Um fluxo pode pedir parametros dentro de
limites aprovados no schema. Valores fora do limite exigem mudanca do motor, testes e review.

## Quem cuida do painel da TV?

- o dono da automacao define significado, meta e acao esperada de cada indicador;
- Plataforma garante coleta, disponibilidade e refresh;
- Seguranca garante que a TV mostre agregados sem dados pessoais;
- Auditoria verifica se o indicador e reproduzivel a partir dos eventos.

## Por que nao usar um SQLite por fluxo?

Porque isso fragmenta concorrencia, backup, consulta e governanca. A POC usa um process
store PostgreSQL unico, separado do metadata DB do Airflow. Cada instancia tem area,
workflow, estado, SLA, assinaturas e responsavel.

## Airflow e o sistema de registro oficial?

Nao. Airflow orquestra. O process store registra o estado operacional da POC; GED, assinatura
e sistemas corporativos continuam sendo fontes oficiais conforme o dominio. Em producao,
os estados precisam ser reconciliados com essas fontes.

## Agentes de IA podem aprovar ou assinar?

Nao. Eles podem propor, criticar, resumir e solicitar revisao. Nao assinam documentos, nao
aprovam efeito financeiro, nao alteram politica e nao executam ferramenta fora de allowlist.

## O que acontece quando uma assinatura nao chega?

O processo permanece `AWAITING_SIGNATURES`, emite lembretes nos intervalos permitidos e,
ao expirar, segue para quarentena ou revisao manual. Nunca existe aprovacao por silencio.

## Como criar um fluxo novo?

1. Copiar uma entrada YAML existente.
2. Definir ownership, objetivo, SLA, entradas, saidas e signatarios.
3. Rodar `make business-catalog test security-check`.
4. Abrir PR e revisar o catalogo gerado.
5. Obter reviews de area, Plataforma e Seguranca conforme impacto.
6. Fazer deploy, acompanhar TV/metricas e reverter se os criterios falharem.

O processo completo esta em [AUTOMATION_PROMOTION.md](AUTOMATION_PROMOTION.md).

## Como alterar o motor?

Criar uma proposta tecnica com ameacas, contrato e rollback; implementar operator/factory
em Python; adicionar testes positivos, negativos, retry e idempotencia; passar pela CI e
por revisao independente. Um YAML nunca ganha campo que execute shell ou codigo arbitrario.

## Quem responde quando algo falha?

- regra ou fila: `area_automation_engineer`;
- schema, evento ou conector: `integration_data_engineer`;
- Airflow, banco, deploy ou capacidade: `orchestration_platform_engineer`;
- acesso, vazamento ou controle: `security_automation_engineer`;
- evidencia/reconstrucao: `audit_reliability_engineer`.

O painel deve sempre apontar a persona responsavel; “TI” e “Negocio” sozinhos nao sao
ownership suficiente.

## Isso ja e producao bancaria?

Nao. E uma POC com controles verificaveis e lacunas declaradas. Producao exige IdP/MFA,
cofre/KMS, SIEM/WORM, backups testados, HA/DR, pentest, hardening, governanca de dados e
validacao formal de Seguranca, Compliance e Juridico.
