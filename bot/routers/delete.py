from aiogram import Router, types, F

from bot.keyboards.main_menu import main_kb
from db.requests.link import delete_link

delete_router = Router()


@delete_router.callback_query(F.data.startswith("del_"))
async def confirm_delete_link(callback: types.CallbackQuery):
    id_link = callback.data.split("_")[1]
    try:
        await delete_link(id_link)
        await callback.message.edit_text("Ссылка успешно удалена.", reply_markup=main_kb())
    except Exception as e:
        await callback.message.answer(f"Ошибка при удалении ссылки: {str(e)}", reply_markup=main_kb())
