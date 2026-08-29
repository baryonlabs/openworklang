"""CLI:  python3 -m openworklang compile <file.work> [--out work.yaml] [--linkml schema.yaml] [--json]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openworklang.compiler import compile_ast_to_work_dict, compile_to_linkml_yaml, work_dict_to_yaml
from openworklang.parser import parse_openworklang


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m openworklang", description="OpenWorkLang (.work) compiler")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compile", help="Compile a .work file into Work IR (work.yaml) and optionally a LinkML schema")
    c.add_argument("source")
    c.add_argument("--out", "-o", help="work.yaml path (default: <stem>.work.yaml next to the source)")
    c.add_argument("--linkml", help="Also write the LinkML schema YAML to this path")
    c.add_argument("--json", action="store_true", help="Print the Work IR as JSON instead of a summary")
    args = parser.parse_args(argv)

    src = Path(args.source)
    if not src.exists():
        print(f"error: source not found: {src}", file=sys.stderr)
        return 2
    ast = parse_openworklang(src)
    work = compile_ast_to_work_dict(ast)
    out = Path(args.out) if args.out else src.with_suffix(".work.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(work_dict_to_yaml(work), encoding="utf-8")
    if args.linkml:
        Path(args.linkml).parent.mkdir(parents=True, exist_ok=True)
        Path(args.linkml).write_text(compile_to_linkml_yaml(ast), encoding="utf-8")
    if args.json:
        print(json.dumps(work, indent=2, ensure_ascii=False))
    else:
        print(f"[OpenWorkLang] {src} -> {out}")
        print(f"  actions:    {', '.join(work['actions'])}")
        print(f"  executors:  " + ", ".join(f"{k}={v['type']}" for k, v in work["executors"].items()))
        print(f"  invariants: {', '.join(work['invariants']) or '-'}")
        if work.get("escalation"):
            print(f"  escalation: " + ", ".join(f"{k}={v}" for k, v in work["escalation"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
