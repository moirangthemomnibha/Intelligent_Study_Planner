from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

from app.modules.settings.schemas import SettingsRead, SettingsUpdate
from app.modules.settings.service import (
    get_or_create_settings,
    update_settings,
)

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)


@router.get("/", response_model=SettingsRead)
def read_settings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_or_create_settings(
        session=session,
        user_id=current_user.id
    )


@router.put("/", response_model=SettingsRead)
def save_settings(
    data: SettingsUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return update_settings(
        session=session,
        user_id=current_user.id,
        data=data
    )