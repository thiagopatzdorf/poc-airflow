from poc.agents import simulated_agent, validate_agent_contract


def test_agents_emit_valid_bound_contracts():
    case = {"case_id": "CASE-DEMO-001", "delta": "12500.00"}
    for role in ("PROPOSER", "CRITIC"):
        validate_agent_contract(simulated_agent(role, case), case)


def test_tampered_agent_contract_is_rejected():
    case = {"case_id": "CASE-DEMO-001", "delta": "12500.00"}
    output = simulated_agent("PROPOSER", case)
    output["recommendation"] = "APPROVE"
    try:
        validate_agent_contract(output, case)
    except ValueError:
        return
    raise AssertionError("tampering should be rejected")

