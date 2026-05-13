from datetime import datetime
from pydantic import BaseModel, Field

# Схема для прийому даних (MQTT)
class VibrationPayload(BaseModel):
    device: str
    rms: float
    peak: float
    p2p: float
    status: str = Field(..., description="OK, WARNING, or CRITICAL")

# Схема для віддачі даних (REST API)
class VibrationResponse(VibrationPayload):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # Дозволяє Pydantic читати дані з моделей SQLAlchemy