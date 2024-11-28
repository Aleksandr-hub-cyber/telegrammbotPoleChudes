import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from quiz_data import API_TOKEN, quiz_data
from database import create_table, get_quiz_index, update_quiz_index, save_result, get_statistics
from handlers import get_question, dp

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    await callback.message.answer(f"Вы ответили: {quiz_data[current_question_index]['options'][correct_option]}")

    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await save_result(user_id, current_question_index)
        await show_statistics(callback.message)

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    await callback.message.answer(f"Вы ответили: {callback.data}")
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await save_result(user_id, current_question_index) 
        await show_statistics(callback.message)

async def show_statistics(message: types.Message):
    stats = await get_statistics()
    if stats:
        stats_message = "Статистика игроков:\n"
        for user_id, score in stats:
            stats_message += f"Пользователь {user_id} - Результат: {score}\n"
        await message.answer(stats_message)
    else:
        await message.answer("Нет доступной статистики.")

async def main():
   
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    