import aiosqlite


async def update_result(user_id):
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Проверяем, есть ли запись для данного пользователя
        async with db.execute('SELECT result FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result is None:
                # Если записи нет, создаем новую с результатом 1
                await db.execute('INSERT INTO quiz_state (user_id, result) VALUES (?, 1)', (user_id,))
            else:
                # Если запись есть, увеличиваем значение result на 1
                await db.execute('UPDATE quiz_state SET result = result + 1 WHERE user_id = ?', (user_id,))
        await db.commit()