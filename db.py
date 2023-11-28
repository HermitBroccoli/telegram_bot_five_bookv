import sqlite3
# import asyncio
# import aiosqlite
from typing import Literal
import json

class Database:
	def __init__(self):
		self.db = "data.db"
		self.conn = sqlite3.connect(self.db)
		self.cur = self.conn.cursor()

	def insert_value(self, chat_id: str, send: Literal[0, 1]):
		query = "INSERT INTO users (chat_id, send_word) VALUES ({}, {})"
		self.cur.execute("INSERT INTO users (chat_id, send_word) VALUES (?, ?)", (chat_id, send))
		self.conn.commit()
	
	def delete_users(self, chat_id: str):
		try:
			self.cur.execute("DELETE FROM users WHERE chat_id = ?", (chat_id))
			self.conn.commit()
		except:
			pass
		
	def list_users(self):
		# ваш код выполнения запроса к базе данных
		# например, если вы используете библиотеку SQLite, это может выглядеть так:
		

		self.cur.execute("SELECT * FROM users")
		rows = self.cur.fetchall()
		users_list = []
		
		for row in rows:
			users_list.append(row[1])
		  # преобразуем объекты Cursor в список словарей
		return users_list