import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from nebula.database import get_db
from nebula.models.transcription import TranscriptionModel
from nebula.schemas.transcription import TranscriptionCreate, TranscriptionResponse

router = APIRouter(prefix="/api/v1/transcriptions", tags=["Transcriptions"])


@router.post("/", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_transcription(payload: TranscriptionCreate, db: Session = Depends(get_db)):
    """Create a single transcription job."""
    job_id = str(uuid.uuid4())

    db_item = TranscriptionModel(
        id=job_id,
        audio_file_path=payload.audio_file_path,
        audio_name=payload.audio_name,
        transcription_name=payload.transcription_name,
        language=payload.language,
        include_timestamps=payload.include_timestamps,
        input_format=payload.input_format,
        output_format=payload.output_format,
        status="queued"
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # TODO: Push job_id into Redis queue here for the background worker

    return db_item


@router.post("/batch", response_model=List[TranscriptionResponse], status_code=status.HTTP_201_CREATED)
def create_transcriptions_batch(payload: List[TranscriptionCreate], db: Session = Depends(get_db)):
    """Create multiple transcription jobs in a single batch (e.g., multi-file drag and drop)."""
    created_items = []

    for audio in payload:
        job_id = str(uuid.uuid4())
        db_item = TranscriptionModel(
            id=job_id,
            audio_file_path=audio.audio_file_path,
            audio_name=audio.audio_name,
            transcription_name=audio.transcription_name,
            language=audio.language,
            include_timestamps=audio.include_timestamps,
            input_format=audio.input_format,
            output_format=audio.output_format,
            status="queued"
        )
        db.add(db_item)
        created_items.append(db_item)

    db.commit()
    for item in created_items:
        db.refresh(item)
        # TODO: Push each item.id into Redis queue here

    return created_items


@router.get("/", response_model=List[TranscriptionResponse])
def list_transcriptions(db: Session = Depends(get_db)):
    """List all transcription jobs."""
    return db.query(TranscriptionModel).all()


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def get_transcription(transcription_id: str, db: Session = Depends(get_db)):
    """Get a single transcription job by its ID (used by frontend to poll status and get results)."""
    item = db.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    return item


@router.put("/{transcription_id}", response_model=TranscriptionResponse)
def update_transcription_name(transcription_id: str, new_name: str, db: Session = Depends(get_db)):
    """Update a transcription job's display name."""
    item = db.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Transcription job not found")

    item.transcription_name = new_name
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcription(transcription_id: str, db: Session = Depends(get_db)):
    """Delete a transcription job record."""
    item = db.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Transcription job not found")

    db.delete(item)
    db.commit()
    return None