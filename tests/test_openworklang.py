from pathlib import Path

import yaml

from openworklang import OpenWorkLangCompiler, compile_ast_to_work_dict, compile_to_linkml_yaml, parse_openworklang
from openworklang.__main__ import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "quality_analysis.work"


def test_parse_example():
    ast = parse_openworklang(EXAMPLE)
    assert ast.name == "quality_analyst"
    assert ast.workflow[:2] == ["collect_data", "detect_anomaly"]
    assert ast.executors["find_correlation"] == "ml"
    assert "verify_sensor_calibration" in ast.invariants


def test_compile_to_work_dict_and_linkml():
    ast = parse_openworklang(EXAMPLE)
    work = compile_ast_to_work_dict(ast)
    assert work["work"] == "quality_analyst"
    assert work["executors"]["detect_anomaly"] == {"type": "rule", "handler": "rules.detect_anomaly"}
    assert work["executors"]["determine_root_cause"]["type"] == "slm"
    assert work["states"][0] == "initialized"
    assert compile_to_linkml_yaml(ast).startswith("id: https://w3id.org/openworkcompiler/schemas/quality_analyst")


def test_params_and_escalation_sections():
    src = """work demo {
  goal: "g"
  params:
    - customer_id
  inputs:
    - crm
  outputs:
    - proposal
  workflow:
    - lookup
    - draft
  executors: {
    lookup: code,
    draft: llm
  }
  escalation: {
    draft: agent,
    on_error: fallback_to_frontier_llm
  }
}"""
    ast = parse_openworklang(src)
    assert ast.params == ["customer_id"] and ast.escalation["draft"] == "agent"
    work = compile_ast_to_work_dict(ast)
    assert work["inputs"] == ["customer_id", "crm"]
    assert work["executors"]["draft"]["type"] == "frontier_llm"
    assert work["escalation"] == {"draft": "agent", "on_error": "fallback_to_frontier_llm"}


def test_cli_writes_yaml(tmp_path):
    out = tmp_path / "q.work.yaml"
    assert main(["compile", str(EXAMPLE), "--out", str(out), "--linkml", str(tmp_path / "q.linkml.yaml")]) == 0
    assert yaml.safe_load(out.read_text())["work"] == "quality_analyst"
    assert OpenWorkLangCompiler().compile_file(EXAMPLE)["actions"][0] == "collect_data"
