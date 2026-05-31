from fastapi import APIRouter
from pydantic import BaseModel

from app.services.settings_service import get_settings_store

router = APIRouter(prefix="/api/settings", tags=["settings"])
store = get_settings_store()


class SetKeyRequest(BaseModel):
    api_key: str


class SetModelRequest(BaseModel):
    base_url: str = ""
    fast_model: str = ""
    reasoning_model: str = ""


@router.get("")
def get_settings():
    return {
        "has_key": store.has_key(),
        "masked_key": store.get_masked_key(),
        "models": store.get_models(),
    }


@router.put("/key")
def set_key(req: SetKeyRequest):
    store.set_key(req.api_key.strip())
    return {"ok": True, "masked_key": store.get_masked_key()}


@router.put("/models")
def set_models(req: SetModelRequest):
    store.set_model_config(
        base_url=req.base_url.strip(),
        fast_model=req.fast_model.strip(),
        reasoning_model=req.reasoning_model.strip(),
    )
    return {"ok": True, "models": store.get_models()}
