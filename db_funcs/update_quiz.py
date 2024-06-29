import aiosqlite


async def update_quiz_index(user_id, index):
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Проверяем, есть ли запись для данного пользователя
        async with db.execute('SELECT * FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            if await cursor.fetchone() is None:
                # Если записи нет, создаем новую с результатом 0
                await db.execute('INSERT INTO quiz_state (user_id, question_index, result) VALUES (?, ?, 0)', (user_id, index))
            else:
                # Если запись есть, обновляем только question_index
                await db.execute('UPDATE quiz_state SET question_index = ? WHERE user_id = ?', (index, user_id))
        await db.commit()