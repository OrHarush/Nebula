from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nebula.database import Base

if TYPE_CHECKING:
    from nebula.models.transcription import TranscriptionModel


class SegmentModel(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    transcription_id: Mapped[str] = mapped_column(ForeignKey("transcriptions.id"), index=True)
    idx: Mapped[int]            # order within the transcription
    start: Mapped[float]        # seconds
    end: Mapped[float]
    text: Mapped[str]

    transcription: Mapped["TranscriptionModel"] = relationship(back_populates="segments")