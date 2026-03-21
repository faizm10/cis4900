"""Optional LLM tutor: explanations only; does not modify mastery or routes."""

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.kc import KC
from app.models.mastery import Mastery
from app.models.route import Route


def _context_block(db: Session, learner_id: str, kc_id: int | None) -> str:
    lines: list[str] = []
    kc_map: dict[int, str] = {kc.kc_id: kc.name for kc in db.query(KC).all()}
    route = db.query(Route).filter(Route.learner_id == learner_id).first()
    if route:
        goal = db.query(KC).filter(KC.kc_id == route.goal_kc_id).first()
        gn = goal.name if goal else "?"
        lines.append(f"Goal concept: {gn}")
        ordered_names = [kc_map.get(i, "?") for i in route.ordered_kc_ids]
        lines.append(f"Ordered route: {' → '.join(ordered_names)}")
        nn = kc_map.get(route.next_kc_id, "?") if route.next_kc_id is not None else "none"
        lines.append(f"Next topic (app-chosen): {nn}")
    else:
        lines.append("No active route in database for this learner.")

    if kc_id is not None:
        kc = db.query(KC).filter(KC.kc_id == kc_id).first()
        if kc:
            lines.append(f"Learner is viewing/practicing topic: {kc.name} (kc_id={kc_id})")
        m = (
            db.query(Mastery)
            .filter(Mastery.learner_id == learner_id, Mastery.kc_id == kc_id)
            .first()
        )
        if m:
            lines.append(f"Estimated mastery P(L) for this topic: {m.p_mastery:.3f}")
        else:
            lines.append("No mastery record yet for this topic (using priors until first attempt).")
    else:
        lines.append("Current topic id not sent by client.")

    return "\n".join(lines)


def tutor_reply(db: Session, learner_id: str, message: str, kc_id: int | None) -> str:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("Tutor is disabled: OPENAI_API_KEY is not set.")

    ctx = _context_block(db, learner_id, kc_id)
    system = (
        "You are a concise computer science tutor. The learning application (not you) decides "
        "which concept the learner practices next and estimates mastery using a fixed policy. "
        "Never tell the learner to skip the app's ordering or claim you changed their path. "
        "Give short, accurate explanations, examples, or debugging hints.\n\n"
        f"Learner context:\n{ctx}"
    )
    user_msg = message.strip() or "In one short paragraph, what should I focus on for this topic?"

    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 500,
        "temperature": 0.5,
    }
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()

    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError("Unexpected response from language model API") from e
