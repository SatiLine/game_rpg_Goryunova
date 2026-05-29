from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    npc_id: str
    npc_name: str
    npc_role: str
    npc_personality: str
    npc_state: str
    npc_long_term_memory: list[str] = Field(default_factory=list)
    game_hour: int = Field(ge=0, le=23)
    player_name: str
    player_hp: int = Field(ge=0, le=100)
    player_gold: int = Field(ge=0)
    player_message: str
    conversation_history: list[dict[str, str]] = Field(default_factory=list)  # ← новое


class PredictResponse(BaseModel):
    npc_id: str
    npc_mood: str
    mood_confidence: float
    dialogue: str


class ModelInfo(BaseModel):
    name: str
    version: str
    description: str
    features: list[str]
    output_classes: list[str]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
