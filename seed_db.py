import asyncio
from sqlalchemy import select
from database import AsyncSessionLocal, Engine, Device, init_db

ENGINES_DATA = [
    ('W22 IE3 0.75 kW 2P 80 3Ph', '3-фазний промисловий', 0.75, 3000.0),
    ('W22 IE3 0.75 kW 4P 80 3Ph', '3-фазний промисловий', 0.75, 1500.0),
    ('W22 IE3 1.5 kW 4P 90L 3Ph', '3-фазний промисловий', 1.5, 1500.0),
    ('W22 IE3 1.5 kW 4P 90L 3Ph (B14T)', '3-фазний промисловий', 1.5, 1500.0),
    ('W22 IE3 2.2 kW 4P 100L 3Ph', '3-фазний промисловий', 2.2, 1500.0),
    ('W22 IE3 3 kW 6P 132S 3Ph', '3-фазний промисловий', 3.0, 1000.0),
    ('W22 IE3 4 kW 4P 112M 3Ph', '3-фазний промисловий', 4.0, 1500.0),
    ('W22 IE3 7.5 kW 4P 132M 3Ph', '3-фазний промисловий', 7.5, 1500.0),
    ('W22 Brake Motor IE1 1.5 kW 4P 90L 3Ph', 'гальмівний промисловий', 1.5, 1500.0),
    ('W22Xdb IE3 7.5 kW 4P 132S/M 3Ph', 'вибухозахищений', 7.5, 1500.0)
]

async def seed():
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # 1. Перевіряємо, чи є вже двигуни в базі
        result = await session.execute(select(Engine).limit(1))
        if not result.scalars().first():
            print("Заповнення каталогу двигунів...")
            for name, eng_type, power, rotate in ENGINES_DATA:
                session.add(Engine(name=name, type=eng_type, power=power, rotate=rotate))
            await session.commit()
            print("✅ Каталог двигунів успішно завантажено!")
        else:
            print("⚡ Каталог двигунів вже існує в БД. Пропускаємо.")

        # 2. Перевіряємо, чи існує тестовий пристрій 'motor_1'
        dev_result = await session.execute(select(Device).where(Device.device_id == "motor_1"))
        if not dev_result.scalars().first():
            print("Створення тестового пристрою 'motor_1'...")
            session.add(Device(device_id="motor_1", engine_id=1, location="Головний конвеєр, Секція А"))
            await session.commit()
            print("✅ Тестовий пристрій 'motor_1' зареєстровано!")
        else:
            print("⚡ Пристрій 'motor_1' вже зареєстрований. Пропускаємо.")

if __name__ == "__main__":
    asyncio.run(seed())