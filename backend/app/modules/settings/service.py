from datetime import datetime, timezone

from sqlmodel import Session, select

from app.modules.settings.models import UserSettings
from app.modules.settings.schemas import SettingsUpdate


def get_or_create_settings(
    session: Session,
    user_id: int
) -> UserSettings:

    statement = select(UserSettings).where(
        UserSettings.user_id == user_id
    )

    settings = session.exec(statement).first()

    if settings:
        return settings

    settings = UserSettings(user_id=user_id)

    session.add(settings)
    session.commit()
    session.refresh(settings)

    return settings


def update_settings(
    session: Session,
    user_id: int,
    data: SettingsUpdate
) -> UserSettings:

    settings = get_or_create_settings(session, user_id)

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if value is not None:
            setattr(settings, key, value)

    settings.updated_at = datetime.now(timezone.utc)

    session.add(settings)
    session.commit()
    session.refresh(settings)

    return settings