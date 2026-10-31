from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TranscriptionCreate(BaseModel):
    """DTO for creating a new transcription job (Command / Request Payload)"""
    audio_file_path: str
    audio_name: str
    transcription_name: Optional[str] = None
    language: Optional[str] = "en"
    include_timestamps: bool = True
    input_format: str
    output_format: str = "txt"

class TranscriptionResponse(TranscriptionCreate):
    """DTO for returning a transcription entity back to the client"""
    id: str
    status: str  # queued, processing, completed, failed
    created_at: datetime
    result_text: Optional[str] = None

    class Config:
        from_attributes = True  # Allows Pydantic to read directly from SQLAlchemy models