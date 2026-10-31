import enum
from datetime import UTC, datetime
from sqlalchemy.orm import Mapped, mapped_column
from nebula.database import Base

class Status(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TranscriptionModel(Base):
    __tablename__ = "transcriptions"

    id: Mapped[str] = mapped_column(primary_key=True)
    audio_file_path: Mapped[str]
    audio_name: Mapped[str]
    transcription_name: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    status: Mapped[Status] = mapped_column(default=Status.QUEUED)
    progress: Mapped[float] = mapped_column(default=0.0)     # 0-100
    error: Mapped[str | None]
    attempts: Mapped[int] = mapped_column(default=0)

    length: Mapped[float | None]                              # audio duration, seconds
    language: Mapped[str | None]                              # requested; None = auto
    detected_language: Mapped[str | None]                     # what Whisper decided
    model: Mapped[str]
    device_used: Mapped[str | None]                           # "cuda" / "cpu"
    include_timestamps: Mapped[bool] = mapped_column(default=True)

    file_size: Mapped[int]                                    # for duplicate detection
    file_mtime: Mapped[float]