import aiosqlite

async def migrate_database():
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Проверяем, есть ли колонка "result" в таблице "quiz_state"
        async with db.execute("PRAGMA table_info(quiz_state)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
            if "result" not in columns:
                # Если колонки "result" нет, добавляем ее
                await db.execute("ALTER TABLE quiz_state ADD COLUMN result INTEGER DEFAULT 0")
                await db.commit()
                print("Column 'result' added to the 'quiz_state' table.")
            else:
                print("Column 'result' already exists in the 'quiz_state' table.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate_database())