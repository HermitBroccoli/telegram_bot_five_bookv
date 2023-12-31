import aiofiles
import aiohttp
import asyncio
import logging
import aiocron
import pytz
import sys
import datetime
import re
from bs4 import BeautifulSoup
import time
from typing import Dict

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.env import EnvVariables
from db import Database

bot = Bot(token=EnvVariables().get_value("TG_TOKEN"))
dp = Dispatcher()

base = Database()

months_dict: Dict[int, str] = {
	1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
	7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12:'декабря'
}

phrases = [
	"Пожалуйста!",
	"Всегда рад помочь!"
	"Не благодари, это для меня удовольствие помогать.",
	"Рад быть полезным!"
]

one_felicitation = (
	"Поздравляем вас с чудесным и ярким праздником - Новым Годом! Желаем вам исполнения всех ваших желаний, пусть удача и добро станут вашими верными спутниками в грядущем году.",
	"Пускай радость и счастье войдут в ваш дом, а ваши сердца наполнятся любовью и теплом. Желаем вам отменного здоровья, грандиозных успехов и покорения новых высот в жизни и во всех начинаниях.",
	"Давайте делиться теплом и поддерживать друг друга, ведь это то, что делает нас особенными! Пусть Новый Год подарит каждому из вас множество ярких моментов, незабываемых встреч и удивительных приключений!",
	"Счастливого Нового Года, дорогие друзья! Пусть праздники пройдут радостно и незабываемо, а каждый день в новом году принесет вам только позитивные эмоции и приятные сюрпризы!"
)



async def new_year(felicitation=None):
	users = base.list_users()

	felicitation = "\n".join(one_felicitation)

	for user in users:
		await bot.send_message(chat_id=user, text=felicitation)


async def get_html():
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get('https://wotpack.ru/slova-iz-5-bukv-tinkoff-otvety-na-segodnja-nojabr/') as response:
				html = await response.text()
				async with aiofiles.open('downloaded.html', 'w', encoding='utf-8') as file:
					await file.write(html)
		# await bot.send_message(chat_id="1295366799", text="hello")
	except Exception as e:
		print(f"An error occurred: {e}")

async def process_html():
	try:
		async with aiofiles.open('downloaded.html', 'r', encoding='utf-8') as file:
			html = await file.read()
			soup = BeautifulSoup(html, 'html.parser')
			current_date = datetime.datetime.now()
			current_month = current_date.month  # Получаем номер текущего месяца

			if current_month in months_dict:
				month_name = months_dict[current_month]  # Получаем название месяца из словаря
				pattern = rf'(\d{{1,2}}\s{month_name}.*?)\.'  # Создаем шаблон регулярного выражения с названием текущего месяца

				for item in soup.find_all('li'):
					if re.search(pattern, item.text, re.IGNORECASE):
						word_match = re.findall(pattern, item.text)
						if word_match:
							word = str(word_match[0])
							last_word = word.split()[-1]
							last_word_without_spaces = last_word.replace(" ", "")
							res = base.list_users()
							for items in res:
								await bot.send_message(chat_id=items, text=f"Привет!\nЯ нашёл новое слово на просторах интернета!\nСлово дня: {last_word_without_spaces}")
								time.sleep(1)
							break  # Для прекращения поиска после первого найденного совпадения
			else:
				print("Не удалось определить текущий месяц")

	except Exception as e:
		print(f"An error occurred while processing HTML: {e}")

@dp.message(Command('yrights'))
async def inc(message: types.Message):
	res = base.list_users()
	print(res)


@dp.message(Command("start"))
async def cms_start(message: types.Message):
	kb = [
		[types.KeyboardButton(text="да")],
		[types.KeyboardButton(text="нет")]
	]
	keyboard = types.ReplyKeyboardMarkup(
		keyboard=kb,
		resize_keyboard=True
	)
	await message.answer("Хотите чтобы вам приходили новые слова?", reply_markup=keyboard)

@dp.message(F.text.lower() == "да")
async def yes_hp(message: types.Message):
	base.insert_value(chat_id=str(message.chat.id), send=1)
	await message.answer(text="Супер! Ты добавлен в список кто будет их получать!", reply_markup=types.ReplyKeyboardRemove())
@dp.message(F.text.lower()=="нет")
async def no_hp(message: types.Message):
	await message.answer(
		text="Очень жаль! Если что жми 'да'. Буду ждать!"
	)

async def send_word_daily():
	await get_html()
	await process_html()

async def main():
	logging.basicConfig(level=logging.INFO)
	await dp.start_polling(bot)

if __name__ == "__main__":
	try:
		loop = asyncio.get_event_loop()
		loop.create_task(main())

		# Устанавливаем часовой пояс Asia/Vladivostok для функции send_word_daily
		aiocron.crontab('0 13 * * *', func=send_word_daily, tz=pytz.timezone('Asia/Vladivostok'))
		aiocron.crontab('0 0 1 1 *', func=new_year, tz=pytz.timezone('Asia/Vladivostok'))
		aiocron.crontab('0 0 1 1 *', func=new_year, tz=pytz.timezone('Europe/Moscow'))

		loop.run_forever()  # Запускаем цикл событий напрямую
	except KeyboardInterrupt:
		sys.exit()