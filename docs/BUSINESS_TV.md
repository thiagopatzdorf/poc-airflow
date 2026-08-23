# Painel das areas — modo TV

O painel `Operacao Documental — TV` foi desenhado para leitura a distancia e atualiza a
cada 10 segundos:

- processos em andamento;
- assinaturas pendentes;
- processos fora do SLA;
- concluidos no dia;
- fila por area;
- tickets recebidos hoje e aderencia ao SLA de 20 minutos;
- série temporal de entradas e últimos tickets processados;
- vinte tickets que exigem atenção, com Processo ID no padrão TKT-AAAAMMDD-NNNNNN.

URL depois da publicacao do Grafana:

`https://honda.tailf3785c.ts.net:8443/d/business-process-tv?kiosk`

## Por que PostgreSQL e nao SQLite por fluxo

SQLite por fluxo criaria varios arquivos, writers concorrentes, backups fragmentados e
consultas ruins entre areas. A POC usa um banco operacional `poc_business`, separado
logicamente do metadata DB do Airflow, com tabelas de instancias e eventos. Isso permite
uma TV consolidada e filtros por area/processo sem misturar dados com o motor do Airflow.

O banco não publica porta. Grafana acessa pela rede interna do Compose com usuario proprio.
Para producao, deve migrar para instancia/cluster dedicado, TLS, backup e credencial
read-only exclusiva para o dashboard.

## Governanca do indicador

Cada card deve ter dono, definicao e acao esperada. A TV nao deve exibir nome, CPF, conta,
conteudo documental ou justificativa sensivel. Identificadores tecnicos ficam restritos à
tela de investigacao autenticada; a visao coletiva mostra somente agregados e filas.

## Loop sintético diário

O DAG synthetic_daily_workload roda a cada dois minutos e converge para uma meta
determinística entre 200 e 400 tickets por dia. Cada rodada cria no máximo doze tickets,
permitindo observar os cards e gráficos subindo durante a apresentação sem sobrecarregar
a Honda. A meta pode ser ajustada por POC_SYNTHETIC_DAILY_MIN e
POC_SYNTHETIC_DAILY_MAX.

Todos esses registros têm is_synthetic=true, IDs iniciados por TKT e eventos com
generator=daily-load-v1. Eles nunca enviam documentos ou mensagens reais. Os DAGs
documentais separados continuam sendo a prova funcional de assinatura humana.
