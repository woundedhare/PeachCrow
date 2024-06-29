import aiosqlite


async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state
         (user_id INTEGER PRIMARY KEY,
          question_index INTEGER,
          result INTEGER DEFAULT 0)''')
        # Сохраняем изменения
        await db.commit()