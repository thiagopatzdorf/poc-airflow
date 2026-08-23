# Motor YAML de documentos

Cada entrada em `config/workflows/document_lifecycle.yaml` gera uma DAG completa:

```text
receber → ler/extrair → validar → enviar → aguardar assinatura 1..N → baixa
```

O schema e fechado: campo desconhecido, identificador invalido, aprovador duplicado,
prazo fora do limite ou quórum inconsistente impedem o carregamento. YAML nunca define
Python, shell, SQL, URL ou ferramenta; ele seleciona somente variaveis de uma maquina de
estados implementada e testada.

## Variaveis atuais

- tipo e nome do fluxo;
- agenda;
- retencao;
- lista ordenada de signatarios;
- prazo de assinatura;
- intervalos e limite de lembretes;
- destino seguro ao expirar.

Na POC, os eventos de envio e assinatura sao simulados pela UI HITL do Airflow. Em uma
integracao real, o mesmo contrato deve consumir callbacks assinados do provedor documental,
com idempotency key, digest do documento e reconciliacao antes de repetir qualquer envio.

