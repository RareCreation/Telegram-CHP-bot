from io import BytesIO

from PIL import Image
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message, BufferedInputFile

from handlers.bot_instance import bot
from states.form import InstructionState

router = Router(name="show_instructions")

def load(dp: Router) -> None:
    dp.include_router(router)


@router.callback_query(F.data == "show_instructions")
async def show_instructions(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📖 Отправьте аватарку для обработки",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
            ]
        )
    )
    await state.set_state(InstructionState.waiting_for_avatar)


@router.message(InstructionState.waiting_for_avatar, F.photo)
async def process_avatar(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    try:
        base_image = Image.open("resources/base.png")
        avatar_image = Image.open(BytesIO(file_bytes.read()))

        avatar_image = avatar_image.resize((85, 85))

        avatar_image_second = avatar_image.resize((100, 100))

        base_image.paste(avatar_image, (1210, 190))

        base_image.paste(avatar_image_second, (1782, 175))

        output_buffer = BytesIO()
        base_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        buffered_file = BufferedInputFile(file=output_buffer.getvalue(), filename="avatar.png")
        await message.answer_photo(photo=buffered_file)

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке изображения: {e}")

    await state.clear()
