"""Optional LLM tutor: explanations only; does not modify mastery or routes."""

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.kc import KC
from app.models.mastery import Mastery
from app.models.route import Route
from app.services.llm_clients import dispatch_llm


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


def format_upstream_error(response: httpx.Response) -> str:
    """Short detail string for HTTP errors from LLM APIs."""
    try:
        body = response.json()
        err = body.get("error")
        if isinstance(err, dict) and "message" in err:
            return str(err["message"])[:500]
        if isinstance(err, str):
            return err[:500]
        if body.get("type") == "error" and isinstance(body.get("error"), dict):
            inner = body["error"]
            if "message" in inner:
                return str(inner["message"])[:500]
        if isinstance(body.get("error"), dict) and "message" in body["error"]:
            return str(body["error"]["message"])[:500]
    except Exception:
        pass
    text = response.text[:500] if response.text else ""
    return text or f"HTTP {response.status_code}"


def _credential_error_message() -> str:
    p = (settings.LLM_PROVIDER or "openai").lower()
    if p == "openai":
        return (
            "Tutor is disabled: set LLM_API_KEY (or OPENAI_API_KEY) for OpenAI-compatible APIs."
        )
    if p == "anthropic":
        return "Tutor is disabled: set ANTHROPIC_API_KEY for Claude."
    if p == "gemini":
        return "Tutor is disabled: set GEMINI_API_KEY for Gemini."
    return "Tutor is disabled: check LLM_PROVIDER and API keys."


def tutor_reply(db: Session, learner_id: str, message: str, kc_id: int | None) -> str:
    provider = (settings.LLM_PROVIDER or "openai").lower()
    if provider == "openai" and not settings.LLM_API_KEY:
        raise RuntimeError(_credential_error_message())
    if provider == "anthropic" and not settings.ANTHROPIC_API_KEY:
        raise RuntimeError(_credential_error_message())
    if provider == "gemini" and not settings.GEMINI_API_KEY:
        raise RuntimeError(_credential_error_message())

    ctx = _context_block(db, learner_id, kc_id)
    system = (
        "You are a concise computer science tutor. The learning application (not you) decides "
        "which concept the learner practices next and estimates mastery using a fixed policy. "
        "Never tell the learner to skip the app's ordering or claim you changed their path. "
        "Give short, accurate explanations, examples, or debugging hints.\n\n"
        f"Learner context:\n{ctx}"
    )
    user_msg = message.strip() or "In one short paragraph, what should I focus on for this topic?"

    return dispatch_llm(system, user_msg)
