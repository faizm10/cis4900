import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import tutor as tutor_service

router = APIRouter()


class TutorChatIn(BaseModel):
    learner_id: str = Field(..., min_length=1, max_length=100)
    message: str = ""
    kc_id: int | None = None


class TutorChatOut(BaseModel):
    reply: str


@router.post("/tutor/chat", response_model=TutorChatOut)
def tutor_chat(payload: TutorChatIn, db: Session = Depends(get_db)):
    try:
        reply = tutor_service.tutor_reply(
            db,
            payload.learner_id,
            payload.message,
            payload.kc_id,
        )
    except RuntimeError as e:
        msg = str(e)
        if (
            "disabled" in msg.lower()
            or "LLM_API_KEY" in msg
            or "OPENAI_API_KEY" in msg
            or "ANTHROPIC_API_KEY" in msg
            or "GEMINI_API_KEY" in msg
        ):
            raise HTTPException(status_code=503, detail=msg) from e
        raise HTTPException(status_code=502, detail=msg) from e
    except httpx.HTTPStatusError as e:
        detail = tutor_service.format_upstream_error(e.response)
        raise HTTPException(
            status_code=502,
            detail=f"Language model API error {e.response.status_code}: {detail}",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail="Tutor request failed") from e

    return TutorChatOut(reply=reply)
