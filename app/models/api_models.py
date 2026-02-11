"""Pydantic models for API request/response (ST-032).

These models mirror contracts/schemas/command.schema.json and
contracts/schemas/decision.schema.json at the API boundary.
Internal pipeline continues to use Dict[str, Any].
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Command sub-models (from command.schema.json) ---

class HouseholdMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    workload_score: Optional[float] = None


class Zone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zone_id: str
    name: str


class ShoppingList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    list_id: str
    name: str


class Household(BaseModel):
    model_config = ConfigDict(extra="forbid")

    household_id: Optional[str] = None
    members: List[HouseholdMember] = Field(min_length=1)
    zones: Optional[List[Zone]] = None
    shopping_lists: Optional[List[ShoppingList]] = None


class Defaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_assignee_id: Optional[str] = None
    default_list_id: Optional[str] = None


class Policies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quiet_hours: Optional[str] = None
    max_open_tasks_per_user: Optional[int] = Field(default=None, ge=0)


class Context(BaseModel):
    model_config = ConfigDict(extra="forbid")

    household: Household
    defaults: Optional[Defaults] = None
    policies: Optional[Policies] = None


CapabilityType = Literal[
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify",
]


class CommandRequest(BaseModel):
    """API input model — mirrors command.schema.json."""

    model_config = ConfigDict(extra="forbid")

    command_id: str
    user_id: str
    timestamp: str
    text: str
    capabilities: List[CapabilityType] = Field(min_length=1)
    context: Context


# --- Decision sub-models (from decision.schema.json) ---

StatusType = Literal["ok", "clarify", "error"]
ActionType = Literal[
    "start_job",
    "propose_create_task",
    "propose_add_shopping_item",
    "clarify",
]


class DecisionResponse(BaseModel):
    """API output model — mirrors decision.schema.json (top-level fields).

    payload is kept as Dict[str, Any] because the internal pipeline
    produces dicts, and jsonschema validates the action-specific shape
    in decision_service.py.
    """

    model_config = ConfigDict(extra="forbid")

    decision_id: str
    command_id: str
    status: StatusType
    action: ActionType
    confidence: float = Field(ge=0, le=1)
    payload: Dict[str, Any]
    explanation: str
    trace_id: str
    schema_version: str
    decision_version: str
    created_at: str
