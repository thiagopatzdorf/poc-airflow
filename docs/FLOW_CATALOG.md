# Catalogo de fluxos de negocio

> Gerado de `config/workflows/document_lifecycle.yaml`. Nao editar manualmente.

Este catalogo permite que Negocio valide objetivo, responsabilidade, SLA, entradas, saidas,
assinaturas e tratamento de excecoes sem precisar interpretar codigo Python.

## Adesao de associado

**Objetivo:** Formalizar a adesao do associado com assinatura das partes.

| Campo | Definicao |
|---|---|
| Area responsavel | Cadastro e Relacionamento |
| Engenheiro dono da automacao | area_automation_engineer |
| Engenheiro de plataforma | orchestration_platform_engineer |
| Engenheiro de seguranca | security_automation_engineer |
| Dona da excecao | Operacoes Documentais |
| SLA | 20 minutos |
| Entrada | proposta_validada, documento_adesao |
| Saida | documento_assinado, baixa_documental |
| Assinaturas obrigatorias | 2 |
| Expiracao | 30 minutos |
| Destino ao expirar | quarantine |

### Signatarios

- Associado (simulado)
- Representante da cooperativa (simulado)

### Etapas

`Receber → Ler e validar → Enviar → Aguardar assinaturas → Baixa documental`

---

## Atualizacao cadastral

**Objetivo:** Coletar aceite do associado para atualizacao cadastral.

| Campo | Definicao |
|---|---|
| Area responsavel | Cadastro |
| Engenheiro dono da automacao | area_automation_engineer |
| Engenheiro de plataforma | orchestration_platform_engineer |
| Engenheiro de seguranca | security_automation_engineer |
| Dona da excecao | Central de Atendimento |
| SLA | 20 minutos |
| Entrada | solicitacao_atualizacao, documento_atualizacao |
| Saida | aceite_assinado, cadastro_liberado |
| Assinaturas obrigatorias | 1 |
| Expiracao | 30 minutos |
| Destino ao expirar | quarantine |

### Signatarios

- Associado (simulado)

### Etapas

`Receber → Ler e validar → Enviar → Aguardar assinaturas → Baixa documental`
