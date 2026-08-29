# OpenWorkLang: Agent Programming Language Specification (v4.0)

**OpenWorkLang** is the high-level declarative Agent Programming Language for OpenWorkCompiler.

While tools like CodeSpeak focus on compiling specs into standard software source code (`Spec -> Code`), **OpenWorkLang** compiles an agent's intent, goal, inputs, outputs, tools, memory policies, process invariants, and action DAGs into executable agent workflows (`OpenWorkLang -> Agent Compiler -> Work IR -> Durable Runtime`).

> **"From Code -> Software to OpenWorkLang -> Compiling Agent Work."**

---

## 1. Core Philosophy & Paradigm Shift

```text
Human Intent / Business Specification
                  │
                  ▼
            OpenWorkLang (.work)
                  │
                  ▼
         OpenWorkLang Compiler
   ┌──────────────┼──────────────┐
   ▼              ▼              ▼
Work IR        LinkML         BEHAVIOR.md
(work.yaml)    (YAML Schema)  (Process Spec)
   │              │              │
   ▼              ▼              ▼
Durable       Semantic       Objective
Runtime       OWL/SHACL      Oracle Gate
```

OpenWorkLang captures 8 core agent primitives:

1. **`work`**: Unique agent work scope identifier.
2. **`goal`**: Natural language business intent and target outcome.
3. **`inputs`**: Data payloads required to trigger execution.
4. **`outputs`**: Expected report artifacts, schemas, or data structures.
5. **`tools`**: Available function calls and API signatures.
6. **`memory`**: Memory policy specifications (`short_term`, `knowledge_base`, `vector_store`).
7. **`invariants`**: Non-negotiable process constraints (`BEHAVIOR.md` rules).
8. **`workflow` & `executors`**: Action step DAG sequence and 8-tier lowering routing (`code`, `rule`, `ml`, `slm`, `frontier_llm`, `human`).

---

## 2. OpenWorkLang Syntax Example (`.work`)

```openworklang
# OpenWorkLang (.work) Example: Production Quality Analyst Agent

work quality_analyst {
  goal: "Analyze production line quality anomaly root causes and generate remediation plans"

  inputs:
    - production_data
    - quality_inspection_data
    - equipment_logs

  outputs:
    - root_cause
    - evidence
    - confidence_score
    - remediation_plan

  tools:
    - query_mes()
    - query_sensor()
    - analyze_statistics()
    - create_report()

  memory:
    - short_term
    - quality_knowledge_base

  invariants:
    - verify_sensor_calibration
    - require_human_approval_for_remediation

  workflow:
    - collect_data
    - detect_anomaly
    - find_correlation
    - determine_root_cause
    - create_report

  executors: {
    collect_data: code,
    detect_anomaly: rule,
    find_correlation: ml,
    determine_root_cause: slm,
    create_report: slm
  }
}
```

---

## 3. Compilation Pipeline & Python API

### Compiling `.work` to `WorkIR` and `LinkML`

```python
from pathlib import Path
from openworklang import parse_openworklang, compile_ast_to_work_dict, compile_to_linkml_yaml


# 1. Parse OpenWorkLang AST
ast = parse_openworklang("examples/quality_analysis.work")

# 2. Compile to WorkIR AST
compiler = OpenWorkLangCompiler()
work_ir = compiler.compile_ast_to_work_ir(ast)

# 3. Export work.yaml definition
save_work_ir(work_ir, "quality_analysis.work.yaml")

# 4. Generate LinkML schema
linkml_yaml = compiler.compile_to_linkml_yaml(ast)
print(linkml_yaml)
```

---

## 4. Relationship with Ecosystem Standards

| Language / Framework | Focus | Role in OpenWorkCompiler |
| :--- | :--- | :--- |
| **CodeSpeak** | Spec → General Software Code | Upstream code generator |
| **Kōdo / AIOS** | AI Agent Compiled Languages | Reference paradigm |
| **OpenWorkLang** | **Agent Work Definition & Lowering** | **Authoring Agent Language (.work)** |
| **LinkML** | Data & Schema Authoring DSL | Authoring schema target |
| **Work IR** | Executable Action DAG (`work.yaml`) | Low-Level Intermediate Representation |
| **BEHAVIOR.md** | Process Evaluation Contract | Invariant specification |
