import sqlite3
from datetime import datetime, timedelta, time, date
from PIL import Image, ImageDraw, ImageFont
from hijri_converter import convert
class DBHelper:

	def __init__(self, db_name):
		self.conn = sqlite3.connect(db_name, check_same_thread=False)
		self.conn.row_factory = sqlite3.Row
		self.cursor = self.conn.cursor()

	def get_regions(self):
		return self.cursor.execute('SELECT `id`, `uz_name`, `oz_name` from `regions` order by `sort_order` asc limit 12').fetchall()

	def get_region(self, region_id):
		return self.cursor.execute('SELECT `id`, `uz_name`, `oz_name`, `farq`, `sequence` from `regions` where id = ?', (region_id,)).fetchone()
	
	def get_region_by_order(self, sequence):
		return self.cursor.execute('SELECT `id`, `uz_name`, `oz_name`, `farq` from `regions` where sequence = ?', (sequence,)).fetchone()

	def get_id_by_seq(self, sequence):
		return self.cursor.execute("SELECT `id` FROM `regions` WHERE `sequence` = ?", (sequence,))


	def get_calendar_by_region(self, dt):
		return self.cursor.execute('SELECT * FROM `ramadan_calendar` where r_date = ?', (dt, )).fetchone()

	def user_exists(self, user_id):
		with self.conn:
			result = self.cursor.execute('SELECT * FROM `users` where user_id = ?', (user_id, )).fetchall()
			return bool(len(result))

	def update_user_info(self, user_id, region_id, user_lang):
		with self.conn:
			return self.cursor.execute("UPDATE `users` SET `region_id` = ?, `user_lang` = ? WHERE `user_id` = ?", (region_id, user_lang, user_id))

	def get_users(self):
		with self.conn:
			return self.cursor.execute("SELECT * FROM `users`").fetchall()

	def get_users_region_id(self, user_id):
		return self.cursor.execute("SELECT `region_id` FROM `users` WHERE `user_id` = ?", (user_id,))

	def get_id_by_region(self, region_id, notifications=True):
		with self.conn:
			return self.cursor.execute("SELECT `user_id` FROM `users` WHERE `region_id` = ? AND `notifications` = ?", (region_id, notifications)).fetchone()

	def get_users_lang(self, user_id):
		return self.cursor.execute("SELECT `user_lang` FROM `users` WHERE `user_id` = ?", (user_id,))

	def add_user(self, user_id, first_name, username, region_id, user_lang):
		with self.conn:
			return self.cursor.execute('INSERT INTO `users` (`user_id`, `first_name`, `username`, `region_id`, `user_lang`) VALUES(?,?,?,?,?)', (user_id, first_name, username, region_id, user_lang)).fetchone()

	def close(self):
		self.conn.close()


date_data = {
	'oz': {
		'arab_oy':{
			1: 'muharram',
			2: 'safar',
			3: 'rabiul avval',
			4: 'rabiul oxir',
			5: 'jumodul avval',
			6: 'jumo-dul oxir',
			7: 'rajab',
			8: 'sha`bon',
			9: 'ramazon',
			10: 'shavval',
			11: 'zulqa`da',
			12: 'zulhijja'
		},
		'world_oy':{
			1: 'yanvar',
			2: 'fevral',
			3: 'mart',
			4: 'aprel',
			5: 'may',
			6: 'iyun',
			7: 'iyul',
			8: 'avgust',
			9: 'sentabr',
			10: 'oktabr',
			11: 'noyabr',
			12: 'dekabr',
		},
		'hafta':{
			0: 'Dushanba',
			1: 'Seshanba',
			2: 'Chorshanba',
			3: 'Payshanba',
			4: 'Juma',
			5: 'Shanba',
			6: 'Yakshanba',
		},
	},
	#Қ қ Ҳ ҳ Ў ў Ғ ғ
	'uz': {
		'arab_oy':{
			1: 'муҳаррам',
			2: 'сафар',
			3: 'рабиъул аввал',
			4: 'рабиус соний',
			5: 'жумодул аввал',
			6: 'жумоус соний',
			7: 'ражаб',
			8: 'шаъбон',
			9: 'рамазон',
			10: 'шаввол',
			11: 'зулқаъда',
			12: 'зулҳижжа'
		},
		'world_oy':{
			1: 'январь',
			2: 'февраль',
			3: 'март',
			4: 'апрель',
			5: 'май',
			6: 'июнь',
			7: 'июль',
			8: 'август',
			9: 'сентябрь',
			10: 'октябрь',
			11: 'ноябрь',
			12: 'декабрь',
		},
		'hafta':{
			0: 'Душанба',
			1: 'Сешанба',
			2: 'Чоршанба',
			3: 'Пайшанба',
			4: 'Жума',
			5: 'Шанба',
			6: 'Якшанба',
		},
	}
}


def time_validation(vaqt):
  check = len(str(vaqt)) == 1
  return "0" + str(vaqt) if check else str(vaqt)


def add_farq(vaqt, fraq):
	timed = time.fromisoformat(vaqt+':00')
	dated = date.fromisoformat('2021-06-17')
	all_date = datetime.combine(dated, timed) + timedelta(minutes=fraq)
	

	return time_validation(all_date.hour) + ":" + time_validation(all_date.minute)


def get_time(calendar, farq):
	raz_vaqt = []
	today = datetime.now() + timedelta(hours=5)
	for v in range(1, 6):
		cfv = ''
		if v == 1:
			cfv = 'fajr'
		elif v == 2:
			cfv = 'peshin'
		elif v == 3:
			cfv = 'asr'
		elif v == 4:
			cfv = 'maghrib'
		elif v == 5:
			cfv = 'hufton'

		my_time = time.fromisoformat(add_farq(calendar[cfv], farq)+':00')
		my_date = date.fromisoformat(calendar['r_date'])
		raznitsa = str(datetime.combine(my_date, my_time) - today).split(':')
		tunim = time_validation(raznitsa[1])
		chas = time_validation(raznitsa[0])
		if raznitsa[0].count('day'):
			raz_vaqt.append('')
		else:
			raz_vaqt.append('(+{}:{})'.format(chas, tunim))

	return raz_vaqt


def make_month_taqvim(farq):
	db = DBHelper('romadon.sqlite')
	farq = int(farq)
	img = Image.open("./images/pillow_image/taqvim_month.jpg")

	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("./images/pillow_fonts/arialbd.ttf", 14)
	fonts = ImageFont.truetype("./images/pillow_fonts/arial.ttf", 14)
	hozir = datetime.now().month
	
	draw.text((75, 24), date_data['oz']['world_oy'][hozir].capitalize(), (0, 0, 0),font=font)
	y = 46
	for x in range(1, 31):
		today = (date.fromisoformat('2021-05-31') + timedelta(days=x)+timedelta(hours=5))
		wek = today.weekday()
		calendar = db.get_calendar_by_region(today)
		if wek == 4:
			draw.text((85, y), str(x), (255, 0, 0), font=font)
			draw.text((125, y), date_data['oz']['hafta'][wek], (255, 0, 0),font=font)
			if add_farq(calendar['fajr'], farq)[0] == '0':
				draw.text((250, y), add_farq(calendar['fajr'], farq)[1:], (255, 0, 0),font=font)
			else:
				draw.text((250, y), add_farq(calendar['fajr'], farq), (255, 0, 0),font=font)

			draw.text((350, y), add_farq(calendar['tong'], farq), (255, 0, 0),font=font)
			draw.text((455, y), add_farq(calendar['peshin'], farq), (255, 0, 0),font=font)
			draw.text((555, y), add_farq(calendar['asr'], farq), (255, 0, 0),font=font)
			draw.text((665, y), add_farq(calendar['maghrib'], farq), (255, 0, 0),font=font)
			draw.text((766, y), add_farq(calendar['hufton'], farq), (255, 0, 0),font=font)
			
		else:
			draw.text((85, y), str(x), (0, 0, 0), font=fonts)
			draw.text((125, y), date_data['oz']['hafta'][wek], (0, 0, 0),font=fonts)
			if add_farq(calendar['fajr'], farq)[0] == '0':
				draw.text((250, y), add_farq(calendar['fajr'], farq)[1:], (0, 0, 0),font=fonts)

			else:
				draw.text((250, y), add_farq(calendar['fajr'], farq), (0, 0, 0),font=fonts)

			draw.text((350, y), add_farq(calendar['tong'], farq), (0, 0, 0),font=fonts)
			draw.text((455, y), add_farq(calendar['peshin'], farq), (0, 0, 0),font=fonts)
			draw.text((555, y), add_farq(calendar['asr'], farq), (0, 0, 0),font=fonts)
			draw.text((666, y), add_farq(calendar['maghrib'], farq), (0, 0, 0),font=fonts)
			draw.text((766, y), add_farq(calendar['hufton'], farq), (0, 0, 0),font=fonts)
	
		y += 20.12
	
	img.save('./images/pillow_image/sample-time.jpg')



def make_img(farq):
	farq = int(farq)
	db = DBHelper('romadon.sqlite')
	today = datetime.now() + timedelta(hours=5)
	calendar = db.get_calendar_by_region(today.date())
	fajr = add_farq(calendar['fajr'], farq)
	tong = add_farq(calendar['tong'], farq)
	peshin = add_farq(calendar['peshin'], farq)
	asr = add_farq(calendar['asr'], farq)
	shom = add_farq(calendar['maghrib'], farq)
	hufton = add_farq(calendar['hufton'], farq)

	img = Image.open("./images/pillow_image/times.jpg")
	draw = ImageDraw.Draw(img)
	week = datetime.now().weekday()
	mon = datetime.now().month
	hata = date_data['oz']['hafta'][week]
	oy = date_data['oz']['world_oy'][mon]
	text = hata + ' ' + str(datetime.now().day) + ' ' + oy + ' 2021'
	
	font = ImageFont.truetype("./images/pillow_fonts/Bodoni Bd BT Bold Italic.ttf", 48)
	
	draw.text((720, 11),text,(255,255,255),font=font)
	
	draw.text((820, 154),fajr,(255,255,255),font=font)
	draw.text((820, 224),tong,(255,255,255),font=font)
	draw.text((820, 290),peshin,(255,255,255),font=font)
	draw.text((820, 361),asr,(255,255,255),font=font)
	draw.text((820, 441),shom,(255,255,255),font=font)
	draw.text((820, 530),hufton,(255,255,255),font=font)
	img.save('./images/pillow_image/sample-out.png')


def get_taqvim(user_text, farq, region, use_lang):
	farq = int(farq)
	db = DBHelper('romadon.sqlite')
	if user_text == '🕖 Bugun' or user_text == '🕖 Бугун':
		today = datetime.now() + timedelta(hours=5)
		calendar = db.get_calendar_by_region(today.date())
		end = {
			'oz_what':'Bugun',
			'uz_what': 'Бугун',
			'oz_tuslash': '\b',
			'uz_tuslash': '\b'
		}
		raz_vaqt = get_time(calendar, farq)
	elif user_text == '🕐 Ertaga' or user_text == '🕐 Эртага':
		today = datetime.now() + timedelta(days=1, hours=5)
		calendar = db.get_calendar_by_region(today.date())
		end = {
			'oz_what':'Ertaga',
			'uz_what':'Эртага',
			'oz_tuslash': 'bo`ladi',
			'uz_tuslash': 'бўлади'
		}
		raz_vaqt = ['', '', '', '', '']
	elif user_text == '🕙 Kecha' or user_text == '🕙 Кеча':
		today = datetime.now() + timedelta(hours=5) - timedelta(days=1)
		calendar = db.get_calendar_by_region(today.date())
		end = {
			'oz_what':'Kecha',
			'uz_what':'Кеча',
			'oz_tuslash': 'edi',
			'uz_tuslash': 'эди'
		}
		raz_vaqt = ['', '', '', '', '']
	week = today.weekday()
	oy = date_data[use_lang]['world_oy'][today.month]
	hafta = date_data[use_lang]['hafta'][week]

	gm = str(convert.Gregorian(today.year, today.month, today.day).to_hijri()).split('-')
	hijri_date = {'year': gm[0], 'month': gm[1], 'day': gm[2]}
	arab_oy = date_data[use_lang]['arab_oy'][int(gm[1])].capitalize()
	if use_lang == 'oz':
		text = '<b>Namoz Taqvimi {}</b>\n\n{}<b> {} {} oyi {}\n{} {}, {} kuni {}, {}</b> vaqti bo`yicha\n\nBomdod vaqti: <b>{} {}</b>\nTong (Quyosh chiqish) vaqti: <b>{}</b>\nPeshin vaqti: <b>{} {}</b>\nAsr vaqti: <b>{} {}</b>\nShom vaqti: <b>{} {}</b>\nHufton vaqti: <b>{} {}</b>'.format(
			today.year, end['oz_what'], hijri_date['day'], arab_oy, hijri_date['year'], today.day, oy, hafta, end['oz_tuslash'], region['oz_name'], add_farq(calendar['fajr'], farq), raz_vaqt[0], add_farq(calendar['tong'], farq), add_farq(calendar['peshin'], farq), raz_vaqt[1], add_farq(calendar['asr'], farq), raz_vaqt[2], add_farq(calendar['maghrib'], farq), raz_vaqt[3], add_farq(calendar['hufton'], farq), raz_vaqt[4])
	elif use_lang == 'uz':
		text = '<b>Намоз Тақвими {}</b>\n\n{}<b> {} {} ойи {}\n{} {}, {} куни {}, {}</b> вақти бўйича\n\nБомдод вақти: <b>{} {}</b>\nТонг (Қуёш чиқиш) вақти: <b>{}</b>\nПешин вақти: <b>{} {}</b>\nАср вақти: <b>{} {}</b>\nШом вақти: <b>{} {}</b>\nҲуфтон вақти: <b>{} {}</b>'.format(
			today.year, end['uz_what'], hijri_date['day'], arab_oy, hijri_date['year'], today.day, oy, hafta, end['uz_tuslash'], region['uz_name'], add_farq(calendar['fajr'], farq), raz_vaqt[0], add_farq(calendar['tong'], farq), add_farq(calendar['peshin'], farq), raz_vaqt[1], add_farq(calendar['asr'], farq), raz_vaqt[2], add_farq(calendar['maghrib'], farq), raz_vaqt[3], add_farq(calendar['hufton'], farq), raz_vaqt[4])
	return text