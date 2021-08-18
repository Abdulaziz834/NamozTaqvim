from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import timedelta, date, datetime
from db_helper import DBHelper, get_time, add_farq, time_validation
db = DBHelper('romadon.sqlite')


def alarm(context):
	sequence = context.job.context
	for x in db.get_id_by_seq(sequence):
		region_id = list(x)[0]

	users = db.get_id_by_region(region_id)

	for ol in (users):
		user_id = ''.join(list(ol))
		print(user_id)
		context.bot.send_message(chat_id=int(user_id), text='<b>Namoz vaqti bo`ldi!</b>\n\nNamozingizni o`qib oling, zero <b><i>Albatta, namoz fahsh va yomonlikdan qaytarur! Albatta, Allohning zikri barcha narsadan ulug‘dir!</i></b> <u><i>(Ankabut surasi, 45 oyat)</i></u>', parse_mode='html')

def get_id(update, context):
	user = update.message.from_user
	update.message.reply_text(user.id)



def filter_time(times):
	if times:
		k = ''.join([s for s in times if s.isdigit() or s == ":"]).split(':')
		return int(k[0]), int(k[1])
	return False

def start(update, context):
	if not context.job_queue.get_jobs_by_name('Timer'):
		#now = datetime.now().date()
		#calendar = db.get_calendar_by_region(now)
		#for x in range(1, 13):
		#	region_info = db.get_region_by_order(x)
		#	for i in range(0, 5):
		#		times = filter_time(get_time(calendar, region_info['farq'])[i])
		#		if times:
		#			konw = timedelta(hours=times[0], minutes=times[1])
		#			context.job_queue.run_once(alarm, konw, name='Timer', context=x)
		context.job_queue.run_once(callback=alarm, when=timedelta(seconds=5), name='Timer', context=11)
		context.job_queue.run_once(callback=alarm, when=timedelta(seconds=15), name='Timer', context=5)
		context.bot.send_message(chat_id=1273666675, text='Done')
	else:
		context.bot.send_message(chat_id=1273666675, text='Timer is already set')

def main():
	up = Updater('1613330175:AAH8dDv9cRWDIeeL1c2aOOe2Joa1M5ZtWIw', use_context=True)

	up.dispatcher.add_handler(CommandHandler('start', start))
	up.dispatcher.add_handler(MessageHandler(Filters.all, get_id))
	up.start_polling()
	up.idle()

if __name__ == '__main__':
	main()
