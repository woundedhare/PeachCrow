import aiosqlite


async def get_result(user_id):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT result FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result is not None:
                return result[0]
            else:
                return 0