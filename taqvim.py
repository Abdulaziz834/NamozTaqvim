#!/usr/bin/python3.9.4
# -*- coding: utf-8 -*-

from random import randint

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

from db_helper import DBHelper, get_time, date_data, get_taqvim, make_img, make_month_taqvim
from datetime import datetime, timedelta, date

OZ_BTN_TODAY, OZ_BTN_YESTERDAY, OZ_BTN_TOMORROW, OZ_BTN_MONTH, OZ_BTN_REGION  = '🕖 Bugun', '🕙 Kecha', '🕐 Ertaga', '🗓 To`liq taqvim', '🇺🇿 Mintaqa'
oz_main_buttons = ReplyKeyboardMarkup([
	[OZ_BTN_TODAY], [OZ_BTN_YESTERDAY, OZ_BTN_TOMORROW], [OZ_BTN_MONTH], [OZ_BTN_REGION]
], resize_keyboard=True)

UZ_BTN_TODAY, UZ_BTN_YESTERDAY, UZ_BTN_TOMORROW, UZ_BTN_MONTH, UZ_BTN_REGION  = '🕖 Бугун', '🕙 Кеча', '🕐 Эртага', '🗓 Тўлиқ тақвим', '🇺🇿 Минтақа'
uz_main_buttons = ReplyKeyboardMarkup([
	[UZ_BTN_TODAY], [UZ_BTN_YESTERDAY, UZ_BTN_TOMORROW], [UZ_BTN_MONTH], [UZ_BTN_REGION]
], resize_keyboard=True)


lang_buttons = ReplyKeyboardMarkup([
	['🇺🇿 O`zbekcha (Lotincha)', 'Узбекча (Кирилча) 🇺🇿']
], resize_keyboard=True)



STATE_REGION = 1
STATE_CALENDAR = 2
User_Lang = 'users_lang'

user_lang = dict()
user_region = dict()
db = DBHelper('romadon.sqlite')
juma_nof = []

def region_buttons(ou):
	regions = db.get_regions()
	buttons = []
	tmp_b = []
	for region in regions:
		tmp_b.append(InlineKeyboardButton(region[ou + '_name'], callback_data=region['id']))
		if len(tmp_b) == 3:
			buttons.append(tmp_b)
			tmp_b = []
	return buttons

def start(update: Update, context: CallbackContext):
	user = update.message.from_user
	user_region[user.id] = None
	
	update.message.reply_html("🌎 Tilni tanlang:\n\n🌎 Тилни танланг:", reply_markup=lang_buttons)
	return User_Lang
	

def select_lang(update, context:CallbackContext):
	user = update.message.from_user
	if update.message.text == '🇺🇿 O`zbekcha (Lotincha)':
		user_lang[User_Lang] = 'oz'
		buttons = region_buttons('oz')
		update.message.reply_html("Assalomu alaykum <b>{}</b>! 👋\n  \n<b>Namoz Taqvimi Bo`tida sizni ko`rib turganimizdan hursandmiz!</b> \n \nBerilgan mintaqalardan birini tanlang 👇".format(user.first_name), reply_markup=InlineKeyboardMarkup(buttons))
	elif update.message.text == 'Узбекча (Кирилча) 🇺🇿':
		user_lang[User_Lang] = 'uz'
		buttons = region_buttons('uz')
		update.message.reply_html('Aссалому алайкум <b>{}</b>! 👋\n  \n<b>Намоз Тақвими Ботида сизни кўриб турганимиздан ҳурсандмиз!</b> \n \nБерилган минтақалардан бирини танланг 👇'.format(user.first_name), reply_markup=InlineKeyboardMarkup(buttons))

	return STATE_REGION

def inline_callback(update: Update, context: CallbackContext):
	query = update.callback_query
	user_id = query.from_user.id
	user_region[user_id] = int(query.data)
	region_id = user_region[user_id]
	use_lang = user_lang[User_Lang]
	if not db.user_exists(user_id):
		if query.from_user.username:
			db.add_user(user_id, query.from_user.first_name, query.from_user.username, region_id, user_lang['users_lang'])
		else:
			db.add_user(user_id, query.from_user.first_name, '-', region_id, user_lang['users_lang'])
	else:
		db.update_user_info(user_id, region_id, use_lang)
	
	region = db.get_region(region_id)
	query.message.delete()

	if use_lang == 'oz':
		query.message.reply_html(
			text='<b>Namoz taqvimi</b> 🗓\n\nSiz <b>{}</b> mintaqasini tanladingiz!\n\nKo`proq ma`lumot olish uchun - /about ni bosing, yoki\nQuydagilardan birini tanlang 👇\n'.
			format(region[use_lang + '_name']),
			reply_markup=oz_main_buttons)
	elif use_lang == 'uz':
		query.message.reply_html(
			text='<b>Намоз тақвими</b> 🗓\n\nСиз <b>{}</b> минтақасини танладингиз!\n\nКўпроқ малумот олиш учун - /about ни босинг, ёки\nҚуйдагилардан бирини танланг 👇\n'.
			format(region[use_lang + '_name']),
			reply_markup=uz_main_buttons)

	return STATE_CALENDAR

def calendar_today(update: Update, context: CallbackContext):
	user = update.message.from_user
	user_id = update.message.from_user.id
	if not user_region[user_id]:
		return STATE_REGION
	region_id = user_region[user_id]
	region = db.get_region(region_id)
	use_lang = user_lang[User_Lang]
	week = (datetime.now() + timedelta(hours=5)).weekday()
	make_img(region['farq'])
	hafta = date_data[use_lang]['hafta'][week]
	user_text = update.message.text

	if week == 4:
		if not user_id in juma_nof:
			random_son = randint(1, 7)
			juma_day = 'images/Juma/Juma' + str(random_son) + '.jpg'
			if use_lang == 'oz':
				juma_soob = "🕋 <b>JUMA AYYOMINGIZ MUBORAK BO`LSIN " + user.first_name.upper() + "!</b> 🌙\n\nAssalomu alaykum.\nAllohning salomi\nPayg`ambar ﷺning duolari\nQuronnig nuri\nJumaning barakasi siz bilan bo`lsin!"
			elif use_lang == 'uz':
				juma_soob = "🕋 <b>ЖУМА АЙЙОМИНГИЗ МУБОРАК БЎЛСИН " + user.first_name.upper() + "!</b> 🌙\n\nАссалому алайкум.\nАллоҳнинг саломи\nПайғамбар ﷺнинг дуолари\nҚуронниг нури\nЖуманинг баракаси сиз билан бўлсин!"
			update.message.reply_photo(photo=open(juma_day, 'rb'), caption=juma_soob, parse_mode='HTML')
			juma_nof.append(user_id)
	update.message.reply_photo(photo=open('images/pillow_image/sample-out.png', 'rb'), caption=get_taqvim(user_text, region['farq'], region, use_lang), parse_mode='html')
	
	if not user.id == 1273666675:
		context.bot.send_message(chat_id=1273666675, text='Hayrli kun *Qirolim!*🤴 \n[{}](tg://user?id={}) ismli odam Ushbu bo\`tdan bugungi ma\`lumotlarni oldi'.format(user.first_name, user_id), parse_mode='Markdown',)

def calendar_yesterday(update: Update, context: CallbackContext):
	user = update.message.from_user
	user_id = update.message.from_user.id
	if not user_region[user_id]:
		return STATE_REGION
	region_id = user_region[user_id]
	region = db.get_region(region_id)
	use_lang = user_lang[User_Lang]
	week = (datetime.now() + timedelta(hours=5) - timedelta(days=1)).weekday()

	hafta = date_data[use_lang]['hafta'][week]
	user_text = update.message.text

	update.message.reply_html(get_taqvim(user_text, region['farq'], region, use_lang))

	if not user.id == 1273666675:
		context.bot.send_message(chat_id=1273666675, text='Hayrli kun *Qirolim!*🤴 \n[{}](tg://user?id={}) ismli odam Ushbu bo\`tdan bugungi ma\`lumotlarni oldi'.format(user.first_name, user_id), parse_mode='Markdown',)

def calendar_tomorrow(update: Update, context: CallbackContext):
	user = update.message.from_user
	user_id = update.message.from_user.id
	if not user_region[user_id]:
		return STATE_REGION
	region_id = user_region[user_id]
	region = db.get_region(region_id)
	use_lang = user_lang[User_Lang]

	week = (datetime.now() + timedelta(days=1, hours=5)).weekday()

	hafta = date_data[use_lang]['hafta'][week]
	user_text = update.message.text

	update.message.reply_html(get_taqvim(user_text, region['farq'], region, use_lang))

	if not user.id == 1273666675:
		context.bot.send_message(chat_id=1273666675, text='Hayrli kun *Qirolim!*🤴 \n[{}](tg://user?id={}) ismli odam Ushbu bo\`tdan bugungi ma\`lumotlarni oldi'.format(user.first_name, user_id), parse_mode='Markdown',)


def calendar_month(update: Update, context: CallbackContext):
	user = update.message.from_user
	user_id = update.message.from_user.id
	if not user_region[user_id]:
		return STATE_REGION
	region_id = user_region[user_id]
	region = db.get_region(region_id)
	use_lang = user_lang[User_Lang]
	make_month_taqvim(region['farq'])
	if use_lang == 'oz':
		hat = '<b>' + date_data['oz']['world_oy'][datetime.now().month].capitalize() + '</b> oyining to`liq taqvimi\nUshbu taqvim <b>' + region['oz_name'] +  '</b> bo`yicha tuzilgan.'
	elif use_lang == 'uz':
		hat = '<b>' + date_data['uz']['world_oy'][datetime.now().month].capitalize() + '</b> ойнинг тўлиқ тақвими\nУшбу тақвим <b>' + region['uz_name'] +  '</b> бўйича тузилган.'
	update.message.reply_photo(photo=open('./images/pillow_image/sample-time.jpg', 'rb'), caption=hat, parse_mode='html')



def select_region(update: Update, context: CallbackContext):
	use_lang = user_lang[User_Lang]
	buttons = region_buttons(use_lang)
	if use_lang == 'oz':
		hat = 'Berilgan mintaqalardan birini tanlang 👇'
	elif use_lang == 'uz':
		hat = 'Берилган минтақалардан бирини танланг 👇'

	update.message.reply_text(hat, reply_markup=InlineKeyboardMarkup(buttons))
	return STATE_REGION

def get_about(update: Update, context: CallbackContext):
	update.message.reply_text('Siz ushbu bo\`tni ma\`lumot oladigan sahifasiga o\`tdingiz!\n\nHamma ma\`lumotlar islom.uz saytidan olingan!\n\n' + 
		'Ushbu bo\`tni admini bilan bog\`lanish uchun [Starcomb](https://t.me/Starcomb) ga yozishingiz mumkin!\n\n' + 
		'Ushbu bo\`t Starcomb tomonidan yaratilgan', parse_mode='Markdown')

#def get_dua(update: Update, context: CallbackContext):
#	use_lang = user_lang[User_Lang]
#	if use_lang == 'oz':
#		duo = '<b>RO`ZA TUTISH SAHARLIK (OG`IZ YOPISH) DUOSI:</b>\nNavvaytu an asuma sovma shahri romazona minal fajri ilal mag`ribi, xolisan lillahi ta`ala. Allohu Akbar!\n\n\n<b>IFTORLIK (OG`IZ OCHISH) DUOSI:</b>\nAllohumma laka sumtu va bika amantu va `alayka tavakkaltu va `ala rizqika aftartu, fag`firli ya g`offaruma qoddamtu va ma axxortu. AMIYN!'
#	elif use_lang == 'uz':
#		# -*- coding: utf-8 -*-
#		duo = '<b>РЎЗА ТУТИШ САҲАРЛИК (ОҒИЗ ЁПИШ) ДУОСИ:</b>\nНаввайту ан асума совма шаҳри ромазона минал фажри илал мариби, холисан лиллаҳи таъала. Аллоҳу Акбар!\n\n\n<b>ИФТОРЛИК (ОҒИЗ ОЧИШ) ДУОСИ:</b>\nАллоҳумма лака сумту ва бика аманту ва ъалайка таваккалту ва ъала ризқика афтарту, фағфирли я ғоффарума қоддамту ва ма аххорту. АМИЙН!'
#
#	update.message.reply_photo(photo=open('images/' + use_lang + '_Ramazon_dua.png', 'rb'), caption=duo, parse_mode='HTML')


def namoz_time(update: Update, context: CallbackContext):
	chat_id = update.message.chat_id
	user_id = update.message.from_user.id
	try:
		use_lang = user_lang[User_Lang]
	except:
		use_lang = list(db.get_users_lang(user_id))
		for xsd in use_lang:
			use_lang = xsd[0]
	if chat_id == 1273666675:
		admin_sob = update.message.text
		if admin_sob == 'Tekshiruv':
			context.bot.send_message(chat_id=chat_id, text='Ushbu bo`t ishlab turibti!',)
		elif admin_sob == 'User List':
			user_list = db.get_users()
			about_users = ''
			num = 1
			for kj in user_list:
				about_users += '{}. {} - <b>{}</b> - @{} - <b>{}</b> \n'.format(str(num), kj[1], str(kj[0]), kj[2], str(kj[3]))
				num += 1
			context.bot.send_message(chat_id=chat_id, text='Ismi - ID - Username - Region_ID \n' + about_users, parse_mode='html')
		else:
			if admin_sob.count('to_users') == 1:
				
				my_mess = ''
				to_user = ''
				remove_comm = admin_sob[8:]
				for dc in remove_comm:
					if not dc.isdigit():
						my_mess += dc
					else:
						to_user += dc
				try:
					user_list = db.get_users()
					users_name = ''
					for kj in user_list:
						if int(kj[0]) == int(to_user):
							users_name = kj[1]
						else:
							continue
					context.bot.send_message(chat_id=int(to_user), text='Salom <b>{}</b>👋!\n{}'.format(users_name, my_mess[2:]), parse_mode='html')
					context.bot.send_message(chat_id=1273666675, text='Yuborildi')
				except Exception as e:
					context.bot.send_message(chat_id=1273666675, text='Hatolik!\n' + str(e))
			elif admin_sob.count('to_everyone') == 1:
				my_mess = admin_sob[12:]
				user_list = db.get_users()
				for kj in user_list:
					try:
						if my_mess == 'Roza tabrigi':
							if kj[-1] == 'oz':
								context.bot.send_photo(chat_id=kj[0], photo=open('images/Ramazon_tabrik.png', 'rb'), caption='Yorishtirib osmonni,\nQo`lga tutib Qur`onni,\nSayqallatib iymonni,\nKelding endi, Romazon.\n\n<b>Kelgan Romazon oyi qutlug` bo`lsin ' + kj[1] + '</b> 🤲', parse_mode='HTML',)
							elif kj[-1] == 'uz':
								context.bot.send_photo(chat_id=kj[0], photo=open('images/Ramazon_tabrik.png', 'rb'), caption='Ёриштириб осмонни,\nҚўлга тутиб Қуръонни,\nСайқаллатиб иймонни,\nКелдинг энди, Рамазон.\n\n<b>Келган Ромазон ойи қутлуғ бўлсин ' + kj[1] + '</b> 🤲', parse_mode='HTML',)

						else:
							context.bot.send_message(chat_id=kj[0], text='Salom <b>{}</b>👋!\n{}'.format(kj[1], my_mess), parse_mode='html')
					except Exception as e:
						context.bot.send_message(chat_id=1273666675, text='Hatolik:\n[{}](tg://user?id={})\n{}'.format(kj[1], kj[0], str(e)), parse_mode='Markdown')
				context.bot.send_message(chat_id=1273666675, text='Yuborildi')

	else:
		
		user_text = update.message.text

		if db.user_exists(user_id):
			if user_text == '🕙 Kecha' or user_text == '🕐 Ertaga' or user_text == '🕙 Кеча' or user_text == '🕐 Эртага':
				user = update.message.from_user
				region_id = list(db.get_users_region_id(user_id))
				for xsd in region_id:
					region_id = xsd[0]
				region = db.get_region(region_id,)

				update.message.reply_html(get_taqvim(user_text, region['farq'], region, use_lang))

				if not user.id == 1273666675:
					context.bot.send_message(chat_id=1273666675, text='Hayrli kun *Qirolim!*🤴 \n[{}](tg://user?id={}) ismli odam Ushbu bo\`tdan bugungi ma\`lumotlarni oldi'.format(user.first_name, user_id), parse_mode='Markdown',)

			#elif user_text == '🤲 Ромазон дуоси' or '🤲 Romazon duosi':
			#	if use_lang == 'oz':
			#		duo = '<b>RO`ZA TUTISH SAHARLIK (OG`IZ YOPISH) DUOSI:</b>\nNavvaytu an asuma sovma shahri romazona minal fajri ilal mag`ribi, xolisan lillahi ta`ala. Allohu Akbar!\n\n\n<b>IFTORLIK (OG`IZ OCHISH) DUOSI:</b>\nAllohumma laka sumtu va bika amantu va `alayka tavakkaltu va `ala rizqika aftartu, fag`firli ya g`offaruma qoddamtu va ma axxortu. AMIYN!'
			#	elif use_lang == 'uz':
			#		duo = '<b>РЎЗА ТУТИШ САҲАРЛИК (ОҒИЗ ЁПИШ) ДУОСИ:</b>\nНаввайту ан асума совма шаҳри ромазона минал фажри илал мариби, холисан лиллаҳи таъала. Аллоҳу Акбар!\n\n\n<b>ИФТОРЛИК (ОҒИЗ ОЧИШ) ДУОСИ:</b>\nАллоҳумма лака сумту ва бика аманту ва ъалайка таваккалту ва ъала ризқика афтарту, фағфирли я ғоффарума қоддамту ва ма аххорту. АМИЙН!'

			#	update.message.reply_photo(photo=open('images/' + use_lang + '_Ramazon_dua.png', 'rb'), caption=duo, parse_mode='HTML')
			elif user_text == '🕖 Bugun' or user_text == '🕖 Бугун':
				user = update.message.from_user
				user_id = update.message.from_user.id

				region_id = list(db.get_users_region_id(user_id))
				for xsd in region_id:
					region_id = xsd[0]
				region = db.get_region(region_id,)
				week = (datetime.now() + timedelta(hours=5)).weekday()
				make_img(region['farq'])
				hafta = date_data[use_lang]['hafta'][week]
				user_text = update.message.text
				
				if week == 4:
					if not user_id in juma_nof:
						random_son = randint(1, 7)
						juma_day = 'images/Juma/Juma' + str(random_son) + '.jpg'
						if use_lang == 'oz':
							juma_soob = "🕋 <b>JUMA AYYOMINGIZ MUBORAK BO`LSIN " + user.first_name.upper() + "!</b> 🌙\n\nAssalomu alaykum.\nAllohning salomi\nPayg`ambar ﷺning duolari\nQuronnig nuri\nJumaning barakasi siz bilan bo`lsin!"
						elif use_lang == 'uz':
							juma_soob = "🕋 <b>ЖУМА АЙЙОМИНГИЗ МУБОРАК БЎЛСИН " + user.first_name.upper() + "!</b> 🌙\n\nАссалому алайкум.\nАллоҳнинг саломи\nПайғамбар ﷺнинг дуолари\nҚуронниг нури\nЖуманинг баракаси сиз билан бўлсин!"
						update.message.reply_photo(photo=open(juma_day, 'rb'), caption=juma_soob, parse_mode='HTML')
						juma_nof.append(user_id)
				update.message.reply_photo(photo=open('images/pillow_image/sample-out.png', 'rb'), caption=get_taqvim(user_text, region['farq'], region, use_lang), parse_mode='html')
				if not user.id == 1273666675:
					context.bot.send_message(chat_id=1273666675, text='Hayrli kun *Qirolim!*🤴 \n[{}](tg://user?id={}) ismli odam Ushbu bo\`tdan bugungi ma\`lumotlarni oldi'.format(user.first_name, user_id), parse_mode='Markdown',)
				
			elif user_text == '🗓 To`liq taqvim' or user_text == '🇺🇿 Mintaqa' or user_text == '🗓 Тўлиқ тақвим' or user_text == '🇺🇿 Минтақа':
				if use_lang == 'oz':
					context.bot.send_message(chat_id=chat_id, text='Ushbu bo`t qayta ishga tushurildi!\nSiz ham /start ni bosib ishga tushiring!')
				elif use_lang == 'uz':
					context.bot.send_message(chat_id=chat_id, text='Ушбу бот қайта ишга тушурилди!\nСиз ҳам /start ни босиб ишга туширинг!')

			else:
				context.bot.forward_message(chat_id=1273666675, from_chat_id=chat_id, message_id=update.message.message_id,)
		else:
			context.bot.send_message(chat_id=chat_id, text='Ushbu bo`t qayta ishga tushurildi!\nSiz ham /start ni bosib ishga tushiring!')




def main():
	updater = Updater('1255876881:AAHM8r6RKsRozKQAnyqYb06ej3anP7bf_nQ', use_context=True,)

	dispatcher = updater.dispatcher

	conv_handler = ConversationHandler(
		entry_points = [CommandHandler('start', start)],
		states={
			User_Lang: [
				MessageHandler(Filters.all, select_lang, pass_user_data=True)
			],
			STATE_REGION: [
				CallbackQueryHandler(inline_callback),
				MessageHandler(Filters.regex('^(' + OZ_BTN_TODAY + ')$'), calendar_today),
				MessageHandler(Filters.regex('^(' + OZ_BTN_YESTERDAY + ')$'), calendar_yesterday),
				MessageHandler(Filters.regex('^(' + OZ_BTN_TOMORROW + ')$'), calendar_tomorrow),
				MessageHandler(Filters.regex('^(' + OZ_BTN_MONTH + ')$'), calendar_month),
				#MessageHandler(Filters.regex('^(' + OZ_BTN_DUA + ')$'), get_dua),
				MessageHandler(Filters.regex('^(' + OZ_BTN_REGION + ')$'), select_region),

				MessageHandler(Filters.regex('^(' + UZ_BTN_TODAY + ')$'), calendar_today),
				MessageHandler(Filters.regex('^(' + UZ_BTN_YESTERDAY + ')$'), calendar_yesterday),
				MessageHandler(Filters.regex('^(' + UZ_BTN_TOMORROW + ')$'), calendar_tomorrow),
				MessageHandler(Filters.regex('^(' + UZ_BTN_MONTH + ')$'), calendar_month),
				#MessageHandler(Filters.regex('^(' + UZ_BTN_DUA + ')$'), get_dua),
				MessageHandler(Filters.regex('^(' + UZ_BTN_REGION + ')$'), select_region)

			],
			STATE_CALENDAR: [
				MessageHandler(Filters.regex('^(' + OZ_BTN_TODAY + ')$'), calendar_today),
				MessageHandler(Filters.regex('^(' + OZ_BTN_YESTERDAY + ')$'), calendar_yesterday),
				MessageHandler(Filters.regex('^(' + OZ_BTN_TOMORROW + ')$'), calendar_tomorrow),
				MessageHandler(Filters.regex('^(' + OZ_BTN_MONTH + ')$'), calendar_month),
				#MessageHandler(Filters.regex('^(' + OZ_BTN_DUA + ')$'), get_dua),
				MessageHandler(Filters.regex('^(' + OZ_BTN_REGION + ')$'), select_region),

				MessageHandler(Filters.regex('^(' + UZ_BTN_TODAY + ')$'), calendar_today),
				MessageHandler(Filters.regex('^(' + UZ_BTN_YESTERDAY + ')$'), calendar_yesterday),
				MessageHandler(Filters.regex('^(' + UZ_BTN_TOMORROW + ')$'), calendar_tomorrow),
				#MessageHandler(Filters.regex('^(' + UZ_BTN_DUA + ')$'), get_dua),
				MessageHandler(Filters.regex('^(' + UZ_BTN_MONTH + ')$'), calendar_month),
				MessageHandler(Filters.regex('^(' + UZ_BTN_REGION + ')$'), select_region)
			],
		},
		fallbacks=[CommandHandler('start', start)]
	)
	message_handler = CommandHandler('about', get_about)

	taqvim_handler = MessageHandler(Filters.all, namoz_time)

	dispatcher.add_handler(conv_handler)
	dispatcher.add_handler(message_handler)
	dispatcher.add_handler(taqvim_handler)

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()