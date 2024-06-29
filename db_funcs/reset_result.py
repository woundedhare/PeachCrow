import aiosqlite

async def reset_result(user_id):
    async with aiosqlite.connect('quiz_bot.db') as db:
        await db.execute('UPDATE quiz_state SET result = 0 WHERE user_id = ?', (user_id,))
        await db.commit()