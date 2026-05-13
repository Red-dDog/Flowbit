from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship

from config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

# 1. Таблиця-довідник моделей двигунів (від колег)
class Engine(Base):
    __tablename__ = "engines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    power = Column(Float, nullable=False)
    rotate = Column(Float, nullable=False)

    # Зв'язок: одна модель може бути встановлена на багатьох пристроях
    devices = relationship("Device", back_populates="engine_model")

# 2. Таблиця конкретних фізичних пристроїв (моторів) на виробництві
class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)  # наприклад, 'motor_1'
    engine_id = Column(Integer, ForeignKey("engines.id"))
    location = Column(String)  # наприклад, 'Цех 1, конвеєр А'

    engine_model = relationship("Engine", back_populates="devices")
    metrics = relationship("VibrationMetric", back_populates="device_info")

# 3. Таблиця метрик вібрації (TimescaleDB)
class VibrationMetric(Base):
    __tablename__ = "vibration_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"), index=True)
    rms = Column(Float)
    peak = Column(Float)
    p2p = Column(Float)
    status = Column(String)

    device_info = relationship("Device", back_populates="metrics")


async def init_db():
    """Створює таблиці в PostgreSQL."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_recent_metrics(limit: int = 50):
    """Вибірка метрик для API."""
    async with AsyncSessionLocal() as session:
        stmt = select(VibrationMetric).order_by(VibrationMetric.timestamp.desc()).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()