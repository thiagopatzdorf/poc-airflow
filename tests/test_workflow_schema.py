from pathlib import Path

import pytest
import yaml

from poc.workflow_schema import business_markdown, parse_workflows

CONFIG = Path(__file__).parents[1] / "config/workflows/document_lifecycle.yaml"


def test_repository_workflows_are_valid():
    flows = parse_workflows(CONFIG)
    assert [flow.id for flow in flows] == ["membership_agreement", "account_update_notice"]
    assert flows[0].required_signatures == 2
    assert "Cadastro e Relacionamento" in business_markdown(flows[0])


def test_unknown_fields_fail_closed(tmp_path):
    raw = yaml.safe_load(CONFIG.read_text())
    raw["workflows"][0]["run_shell"] = "curl attacker"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="unknown fields"):
        parse_workflows(path)


def test_duplicate_approver_is_rejected(tmp_path):
    raw = yaml.safe_load(CONFIG.read_text())
    raw["workflows"][0]["signature"]["signers"][1]["airflow_user"] = "admin"
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="distinct"):
        parse_workflows(path)
