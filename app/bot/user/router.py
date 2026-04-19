from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from app.bot.user.schemas import SUser
from app.dao.dao import UserDAO

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_data = message.from_user
    user_id = user_data.id
    user_info = await UserDAO(session_with_commit).find_one_or_none_by_id(user_id)
    if user_info is None:
        user_schema = SUser(id=user_id, first_name=user_data.first_name,
                            last_name=user_data.last_name, username=user_data.username)
        await UserDAO(session_with_commit).add(user_schema)
    text = ("👋 Добро пожаловать в freedom VPN \n"
            "Используйте клавиатуру ниже, чтобы скачать клиент и подключиться")
    await message.answer(text, reply_markup=main_user_kb(user_id))


