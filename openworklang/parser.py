"""OpenWorkLang Source Parser.

Parses OpenWorkLang (.work) source code strings or files into OpenWorkLangAST.
"""

from __future__ import annotations

import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Union

from openworklang.ast import OpenWorkLangAST


def parse_openworklang(source: Union[str, Path]) -> OpenWorkLangAST:
    """Parse an OpenWorkLang (.work) file or source string into an AST."""
    content = ""
    if isinstance(source, Path) or (isinstance(source, str) and os.path.exists(source)):
        content = Path(source).read_text(encoding="utf-8")
    else:
        content = str(source)

    # 1. Try parsing YAML syntax directly first
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict) and ("work" in data or "name" in data):
            name = data.get("work") or data.get("name")
            return OpenWorkLangAST(
                name=name,
                version=str(data.get("version", "4.0")),
                goal=data.get("goal"),
                inputs=data.get("inputs", []),
                outputs=data.get("outputs", []),
                tools=data.get("tools", []),
                memory=data.get("memory", []),
                invariants=data.get("invariants", []),
                workflow=data.get("workflow", []),
                dependencies=data.get("dependencies", {}),
                executors=data.get("executors", {}),
                params=data.get("params", []),
                escalation={k: str(v) for k, v in (data.get("escalation") or {}).items()},
            )
    except Exception:
        pass

    # 2. Parse Custom DSL Syntax (`work <name> { ... }`)
    work_match = re.search(r"work\s+([a-zA-Z0-9_\-]+)\s*\{(.*)\}", content, re.DOTALL)
    if not work_match:
        raise ValueError("Invalid OpenWorkLang syntax: missing 'work <name> { ... }' block header")

    name = work_match.group(1).strip()
    body = work_match.group(2)

    def extract_scalar(key: str) -> str:
        pattern = re.compile(key + r"\s*:\s*[\"']?([^\"\';\n]+)[\"']?")
        match = pattern.search(body)
        return match.group(1).strip() if match else ""

    def extract_list(key: str) -> list[str]:
        pattern = re.compile(key + r"\s*:\s*\[(.*?)\]", re.DOTALL)
        block_match = pattern.search(body)
        if block_match:
            raw = block_match.group(1)
            items = [item.strip().strip("'\"") for item in raw.split(",") if item.strip()]
            return items
        
        bullet_pattern = re.compile(key + r"\s*:\s*\n((?:\s*[\-\*].*\n)+)")
        bullet_match = bullet_pattern.search(body)
        if bullet_match:
            raw_bullets = bullet_match.group(1)
            items = [
                re.sub(r"^\s*[\-\*]\s*", "", line).strip().strip("'\"")
                for line in raw_bullets.splitlines()
                if line.strip()
            ]
            return items

        arrow_pattern = re.compile(key + r"\s*:\s*(.+)")
        arrow_match = arrow_pattern.search(body)
        if arrow_match and "->" in arrow_match.group(1):
            raw_chain = arrow_match.group(1).split("\n")[0]
            return [s.strip() for s in raw_chain.split("->") if s.strip()]

        return []

    def extract_dict(key: str) -> dict[str, str]:
        pattern = re.compile(key + r"\s*:\s*\{(.*?)\}", re.DOTALL)
        block_match = pattern.search(body)
        res = {}
        if block_match:
            raw = block_match.group(1)
            for line in raw.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    res[k.strip()] = v.strip().strip("'\",")
            return res
        
        dict_bullet_pattern = re.compile(key + r"\s*:\s*\n((?:\s*[a-zA-Z0-9_\-]+\s*:.*\n)+)")
        dict_bullet_match = dict_bullet_pattern.search(body)
        if dict_bullet_match:
            for line in dict_bullet_match.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    res[k.strip()] = v.strip().strip("'\",")
            return res
        return res

    goal = extract_scalar("goal")
    inputs = extract_list("inputs")
    outputs = extract_list("outputs")
    tools = extract_list("tools")
    memory = extract_list("memory")
    invariants = extract_list("invariants")
    workflow = extract_list("workflow")
    executors = extract_dict("executors")
    params = extract_list("params")
    escalation = extract_dict("escalation")

    dependencies = {}
    if len(workflow) > 1:
        for i in range(1, len(workflow)):
            dependencies[workflow[i]] = [workflow[i - 1]]

    return OpenWorkLangAST(
        name=name,
        version="4.0",
        goal=goal or None,
        inputs=inputs,
        outputs=outputs,
        tools=tools,
        memory=memory,
        invariants=invariants,
        workflow=workflow,
        dependencies=dependencies,
        executors=executors,
        params=params,
        escalation=escalation,
    )
