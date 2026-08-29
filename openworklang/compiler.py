"""OpenWorkLang compiler: AST → Work IR dictionary (work.yaml) and LinkML schema.

The output dictionary follows the OpenWorkCompiler Work IR schema (work, version,
description, inputs, outputs, states, actions, dependencies, invariants, executors,
escalation) but is plain data — no runtime types are imported here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from openworklang.ast import OpenWorkLangAST
from openworklang.parser import parse_openworklang

EXECUTOR_TIERS = ("code", "rule", "http", "ml", "slm", "frontier_llm", "human")


def _executor_for(ast: OpenWorkLangAST, action: str) -> Dict[str, Any]:
    tier = ast.executors.get(action, "code").lower()
    if tier == "llm":
        tier = "frontier_llm"
    if tier not in EXECUTOR_TIERS:
        tier = "code"
    spec: Dict[str, Any] = {"type": tier}
    if tier == "code":
        spec["handler"] = f"services.{action}"
    elif tier == "rule":
        spec["handler"] = f"rules.{action}"
    if tier == "slm":
        spec["preferred"] = f"models/{ast.name}-{action}-slm"
    if tier in ("slm", "frontier_llm"):
        spec["fallback"] = ["frontier_llm", "human"]
    return spec


def compile_ast_to_work_dict(ast: OpenWorkLangAST) -> Dict[str, Any]:
    """Compile an AST into a Work IR dictionary (the content of work.yaml)."""
    actions = ast.workflow or list(ast.executors.keys())
    if not actions and ast.tools:
        actions = [t.split("(")[0].strip() for t in ast.tools]
    inputs = list(ast.params) + [i for i in ast.inputs if i not in ast.params]
    work: Dict[str, Any] = {
        "work": ast.name,
        "version": ast.version,
        "description": ast.goal or f"Compiled OpenWorkLang agent work definition for '{ast.name}'",
        "inputs": inputs or ["request_data"],
        "outputs": list(ast.outputs) or ["result"],
        "states": ["initialized"] + [f"{a}_completed" for a in actions],
        "actions": list(actions),
        "dependencies": {k: list(v) for k, v in ast.dependencies.items()},
        "invariants": list(ast.invariants),
        "executors": {a: _executor_for(ast, a) for a in actions},
    }
    if ast.escalation:
        work["escalation"] = dict(ast.escalation)
    return work


def compile_to_linkml_yaml(ast: OpenWorkLangAST) -> str:
    """Compile an AST into a LinkML authoring schema (YAML text)."""
    class_prefix = "".join(part.title() for part in ast.name.replace("-", "_").split("_"))
    lines = [
        f"id: https://w3id.org/openworkcompiler/schemas/{ast.name}",
        f"name: {ast.name}",
        f"description: {ast.goal or 'OpenWorkLang compiled schema'}",
        "imports:",
        "  - linkml:types",
        "classes:",
        f"  {class_prefix}Input:",
        "    slots:",
    ]
    lines += [f"      - {i}" for i in ast.inputs]
    lines += [f"  {class_prefix}Output:", "    slots:"]
    lines += [f"      - {o}" for o in ast.outputs]
    lines.append("slots:")
    for field in dict.fromkeys(ast.inputs + ast.outputs):
        lines += [f"  {field}:", "    range: string", "    required: false"]
    return "\n".join(lines)


def work_dict_to_yaml(work: Dict[str, Any]) -> str:
    return yaml.safe_dump(work, sort_keys=False, allow_unicode=True)


class OpenWorkLangCompiler:
    """Object-style facade over the module functions."""

    def compile_ast_to_work_dict(self, ast: OpenWorkLangAST) -> Dict[str, Any]:
        return compile_ast_to_work_dict(ast)

    def compile_to_linkml_yaml(self, ast: OpenWorkLangAST) -> str:
        return compile_to_linkml_yaml(ast)

    def compile_file(self, source_path: Union[str, Path], output_work_yaml: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        ast = parse_openworklang(source_path)
        work = compile_ast_to_work_dict(ast)
        if output_work_yaml:
            Path(output_work_yaml).parent.mkdir(parents=True, exist_ok=True)
            Path(output_work_yaml).write_text(work_dict_to_yaml(work), encoding="utf-8")
        return work
