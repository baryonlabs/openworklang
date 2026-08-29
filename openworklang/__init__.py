"""OpenWorkLang — a declarative agent programming language (.work).

A .work file states the WHAT of an agent work (goal, inputs, outputs, tools, invariants,
workflow) and the HOW (executor tier per action, run-time params, escalation limits).
This package parses .work sources and compiles them into a Work IR dictionary
(work.yaml) and a LinkML schema. It has no dependency on a runtime; OpenWorkCompiler
consumes the Work IR dict.
"""

from openworklang.ast import OpenWorkLangAST
from openworklang.parser import parse_openworklang
from openworklang.compiler import OpenWorkLangCompiler, compile_ast_to_work_dict, compile_to_linkml_yaml

__version__ = "0.1.0"
__all__ = ["OpenWorkLangAST", "parse_openworklang", "OpenWorkLangCompiler", "compile_ast_to_work_dict", "compile_to_linkml_yaml"]
