"""OpenWorkLang Abstract Syntax Tree (AST) AST Model Definitions.

Defines AST structures for OpenWorkLang domain-specific language (DSL) files.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OpenWorkLangAST(BaseModel):
    """Canonical AST representation of an OpenWorkLang (.work) file."""

    name: str = Field(..., description="Unique name of the work definition")
    version: str = Field(default="4.0", description="OpenWorkLang specification version")
    goal: Optional[str] = Field(default=None, description="Primary business goal or agent intent")
    inputs: List[str] = Field(default_factory=list, description="Input parameters or datasets")
    outputs: List[str] = Field(default_factory=list, description="Expected outputs or report artifacts")
    tools: List[str] = Field(default_factory=list, description="Available tool function signatures")
    memory: List[str] = Field(default_factory=list, description="Memory policies (short_term, knowledge_base)")
    invariants: List[str] = Field(default_factory=list, description="Process invariants and behavior constraints")
    workflow: List[str] = Field(default_factory=list, description="Ordered action DAG steps")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Action dependency DAG")
    executors: Dict[str, str] = Field(default_factory=dict, description="Executor routing mapping (code, rule, ml, slm, llm, human)")
    params: List[str] = Field(default_factory=list, description="Run-time parameters a front agent binds from the request (e.g. customer_id)")
    escalation: Dict[str, str] = Field(default_factory=dict, description="Explicit limits: which actions stay with an agent/model and the global on_error / on_quality_drop / on_timeout policies")

    def to_dict(self) -> Dict[str, Any]:
        """Dump AST to dictionary."""
        return self.model_dump(exclude_none=True)
