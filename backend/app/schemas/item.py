from pydantic import BaseModel, Field


class Choice(BaseModel):
    label: str
    text: str


class ItemBase(BaseModel):
    kc_id: int
    prompt: str
    type: str = Field(..., pattern="^(multiple_choice|free_text)$")
    choices: list[Choice] | None = None
    answer: str
    difficulty: float = Field(0.5, ge=0.0, le=1.0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    prompt: str | None = None
    type: str | None = Field(None, pattern="^(multiple_choice|free_text)$")
    choices: list[Choice] | None = None
    answer: str | None = None
    difficulty: float | None = Field(None, ge=0.0, le=1.0)


class ItemOut(BaseModel):
    item_id: int
    kc_id: int
    prompt: str
    type: str
    choices: list[Choice] | None = None
    difficulty: float

    model_config = {"from_attributes": True}


# Public-facing item (no answer field)
class ItemPublic(BaseModel):
    item_id: int
    kc_id: int
    prompt: str
    type: str
    choices: list[Choice] | None = None
    difficulty: float

    model_config = {"from_attributes": True}


class ItemWithAnswer(ItemOut):
    answer: str
