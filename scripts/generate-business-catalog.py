#!/usr/bin/env python3
"""Gera a visao amigavel revisada pelas areas de negocio."""
from pathlib import Path
from poc.workflow_schema import business_markdown, parse_workflows

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "config/workflows/document_lifecycle.yaml"
target = ROOT / "docs/FLOW_CATALOG.md"
flows = parse_workflows(source)
header = """# Catalogo de fluxos de negocio

> Gerado de `config/workflows/document_lifecycle.yaml`. Nao editar manualmente.

Este catalogo permite que Negocio valide objetivo, responsabilidade, SLA, entradas, saidas,
assinaturas e tratamento de excecoes sem precisar interpretar codigo Python.

"""
target.write_text(header + "\n---\n\n".join(business_markdown(flow) for flow in flows), encoding="utf-8")
print(f"{len(flows)} fluxos escritos em {target}")

