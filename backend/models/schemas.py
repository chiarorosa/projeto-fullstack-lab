from pydantic import BaseModel
from typing import Literal, Optional


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    graph_json: dict  # The full ReactFlow graph object


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph_json: Optional[dict] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    graph_json: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ExecuteRequest(BaseModel):
    task_input: Optional[str] = None
    task_inputs: Optional[list[str]] = None

    def normalized_task_inputs(self) -> list[str]:
        normalized: list[str] = []

        if self.task_input:
            single = self.task_input.strip()
            if single:
                normalized.append(single)

        if self.task_inputs:
            for item in self.task_inputs:
                value = item.strip()
                if value:
                    normalized.append(value)

        return normalized


ProviderType = Literal[
    "openai",
    "anthropic",
    "google",
    "local",
    "openrouter",
    "opencode",
]


class ProviderTestRequest(BaseModel):
    provider: ProviderType
    api_key: Optional[str] = None
    credential_ref: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


class ProviderTestResponse(BaseModel):
    ok: bool
    message: str


class TeamRunResponse(BaseModel):
    id: int
    team_id: int
    execution_id: str
    task_index: int
    task_input: str
    final_output: Optional[str]
    status: str
    error_message: Optional[str]
    selected_agent_id: Optional[str]
    selected_agent: Optional[str]
    selected_provider: Optional[str]
    selected_model: Optional[str]
    routing_reason: Optional[str]
    decision_json: Optional[dict]
    routing_json: Optional[dict]
    created_at: str

    class Config:
        from_attributes = True
