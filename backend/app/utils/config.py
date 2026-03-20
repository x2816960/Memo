from sqlalchemy.orm import Session
from app.models.system_config import SystemConfig
from app.database import SessionLocal

DEFAULT_CONFIG = {
    "image_max_size": "10485760",  # 10MB
    "video_max_size": "209715200",  # 200MB
    "other_max_size": "52428800",  # 50MB
    "max_attachments_per_task": "10"
}


def get_config(db: Session, key: str) -> str:
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if config:
        return config.value
    return DEFAULT_CONFIG.get(key, "")


def update_config(db: Session, key: str, value: str) -> SystemConfig:
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if config:
        config.value = value
    else:
        config = SystemConfig(key=key, value=value)
        db.add(config)
    db.commit()
    db.refresh(config)
    return config


def init_default_config(db: Session):
    for key, value in DEFAULT_CONFIG.items():
        if not db.query(SystemConfig).filter(SystemConfig.key == key).first():
            db.add(SystemConfig(key=key, value=value))
    db.commit()
