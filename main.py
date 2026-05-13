import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import aiomqtt
from pydantic import ValidationError

from config import settings
from schemas import VibrationPayload, VibrationResponse
from database import init_db, AsyncSessionLocal, VibrationMetric, get_recent_metrics

async def save_metric_to_db(data: VibrationPayload):
    """Функція запису валідованих даних у PostgreSQL."""
    async with AsyncSessionLocal() as session:
        metric = VibrationMetric(
            device_id=data.device,  # <── ЗМІНИЛИ ТУТ (було device=data.device)
            rms=data.rms,
            peak=data.peak,
            p2p=data.p2p,
            status=data.status
        )
        session.add(metric)
        await session.commit()
        print(f"💾 Запис збережено в БД! ID: {metric.id}")
        
async def mqtt_consumer():
    while True:
        try:
            async with aiomqtt.Client(hostname=settings.mqtt_broker_host, port=settings.mqtt_broker_port) as client:
                await client.subscribe(settings.mqtt_topic)
                print(f"✅ Успішно підписано на MQTT топік: {settings.mqtt_topic}")
                
                async for message in client.messages:
                    payload_str = message.payload.decode()
                    try:
                        data = VibrationPayload.model_validate_json(payload_str)
                        print(f"\n📊 Валідація успішна! Пристрій: {data.device} | Статус: {data.status}")
                        
                        # ─── ВИКЛИКАЄМО ЗБЕРЕЖЕННЯ В БД ───
                        await save_metric_to_db(data)
                        
                        if data.status in ["WARNING", "CRITICAL"]:
                            print(f"⚠️ УВАГА! Виявлено аномалію ({data.status}).")

                    except ValidationError as e:
                        print(f"❌ [Помилка] Прийшов невалідний JSON")
                        
        except aiomqtt.MqttError as error:
            print(f"⚠️ Втрачено зв'язок з MQTT. Перепідключення...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Помилка: {e}")
            await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ─── ІНІЦІАЛІЗУЄМО БАЗУ ДАНИХ ПРИ СТАРТІ ───
    await init_db()
    print("🗄️ Базу даних ініціалізовано.")
    
    consumer_task = asyncio.create_task(mqtt_consumer())
    yield
    consumer_task.cancel()

app = FastAPI(lifespan=lifespan, title="Flowbit IIoT Server")

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/api/v1/metrics", response_model=list[VibrationResponse])
async def read_metrics(limit: int = 20):
    """Повертає історію останніх вимірювань для дашборду/додатка."""
    metrics = await get_recent_metrics(limit=limit)
    return metrics