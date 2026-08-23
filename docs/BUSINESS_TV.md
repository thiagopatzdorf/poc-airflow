# Painel das areas — modo TV

O painel `Operacao Documental — TV` foi desenhado para leitura a distancia e atualiza a
cada 30 segundos:

- processos em andamento;
- assinaturas pendentes;
- processos fora do SLA;
- concluidos no dia;
- fila por area;
- vinte processos que exigem atencao, ordenados pelo prazo.
- persona de engenharia responsavel por cada processo pendente.

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
