import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import aiosqlite

from question_data.quiz_data import quiz_data
from db_funcs.create import create_table
from db_funcs.get_quiz import get_quiz_index
from db_funcs.update_quiz import update_quiz_index
from db_funcs.update_result import update_result
from db_funcs.get_result import get_result
from db_funcs.reset_result import reset_result
from quiz_funcs.quiz_funcs import new_quiz, get_question, generate_options_keyboard
from tokens import API_TOKEN

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await reset_all_user_data(message.from_user.id)

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Привет! Я бот для проведения квиза", reply_markup=builder.as_markup(resize_keyboard=True))
    await message.answer_sticker("CAACAgIAAxkBAAEMZkVmf70qI2M6Jgzwz34IGOXuWYDj1wACbwADwZxgDMsOfYvA3U1WNQQ")


async def reset_all_user_data(user_id):
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Сбрасываем значения всех колонок для данного пользователя
        await db.execute('UPDATE quiz_state SET question_index = 0, result = 0 WHERE user_id = ?', (user_id,))
        await db.commit()


@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)


@dp.callback_query(F.data.startswith("right_"))
async def right_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    chosen_option = int(callback.data.split("_")[1])
    # Отправляем в чат сообщение, что ответ верный и выбранный вариант
    await callback.message.answer(
        f"Вы выбрали: {quiz_data[current_question_index]['options'][chosen_option]}\nВерно!")
    await callback.message.answer_sticker("CAACAgIAAxkBAAEMZklmf73-Dn16N_vYSECKl5oFKpMWsQACgAADwZxgDDUiPX15tvOeNQQ")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    await update_result(callback.from_user.id)
    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        result = await get_result(callback.from_user.id)
        # Уведомление об окончании квиза с результатом
        await asyncio.sleep(3)
        await callback.message.answer(f"Квиз завершен! Вы ответили правильно на {result} вопросов из 10.")
        await callback.message.answer_sticker("CAACAgIAAxkBAAEMZk1mf7__F6pr81oEcbHCi7JGAWB_gQAChgADwZxgDOa4iNxdyRwENQQ")
        await reset_result(callback.from_user.id)


@dp.callback_query(F.data.startswith("wrong_"))
async def wrong_answer(callback: types.CallbackQuery):
    # Получение текущего вопроса для данного пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)

    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    correct_option = quiz_data[current_question_index]['correct_option']
    chosen_option = int(callback.data.split("_")[1])

    # Отправляем в чат сообщение об ошибке с указанием выбранного варианта и правильного ответа
    await callback.message.answer(f"Вы выбрали: {quiz_data[current_question_index]['options'][chosen_option]}\nНеправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    await callback.message.answer_sticker("CAACAgIAAxkBAAEMZktmf77iv0Du5FxoWMcDLtuddWt3vgACdQADwZxgDDA1Zd15EjDENQQ")
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        result = await get_result(callback.from_user.id)
        await asyncio.sleep(3)
        # Уведомление об окончании квиза с результатом
        await callback.message.answer(f"Квиз завершен! Вы ответили правильно на {result} вопросов из 10.")
        await callback.message.answer_sticker("CAACAgIAAxkBAAEMZk1mf7__F6pr81oEcbHCi7JGAWB_gQAChgADwZxgDOa4iNxdyRwENQQ")
        await reset_result(callback.from_user.id)


async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
