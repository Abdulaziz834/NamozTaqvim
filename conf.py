from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, constants
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

#GROUP_ID = -1001376670344
#censor = ['fuck', 'jala', 'yiba', 'oneni', 'am', 'qoto', 'qo`to', 'dalba', 'ёбта', 'долба', 'ебан', 'сука', 'хуй', 'shit', 'damn', 'dick', 'pussy', 'suka']
#domains = ['.com', '.net', '.org', '.ru', '.me', '.uz', '.gov', '.io']
#
#def is_admin(list_of_admin, chat_id):
#	admins_id = []
#	for x in (list_of_admin):
#		admins_id.append(x['user']['id'])
#	if chat_id in admins_id:
#		return True
#	return False
#
#def is_banned(user_message, ls):
#	user_message = user_message.lower()
#	p = 0
#	for asm in ls:
#		if user_message.count(asm):
#			p += 1
#	return bool(p)
#
#
#def salom(update:Update, context:CallbackContext):
#	user = update.message.from_user
#	if (is_admin(context.bot.get_chat_administrators(update.effective_chat.id), user.id)):
#		update.message.reply_text('Hello admin')
#		update.message.reply_text(update.message.chat_id)
#	else:
#		update.message.reply_text('Hello user')
#
#def delete_sys(update:Update, context:CallbackContext):
#	user = update.message.from_user
#	if update.message.new_chat_members:
#		new_user = list(update.message.new_chat_members)
#		context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
#		context.bot.send_message(chat_id=GROUP_ID, text='Hello <b>'+new_user[0]['first_name'] + '</b>\nWe glad to see you in this group!', parse_mode='html')
#	if is_banned(update.message.text, censor):
#		context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
#		context.bot.send_message(chat_id=GROUP_ID, text="<b>"+update.message.from_user.first_name + '</b>, don`t use a volgar words, otherwise you will get banned!', parse_mode='html')
#		context.bot.restrict_chat_member(chat_id=GROUP_ID, user_id=user.id, permissions=None, until_date=time()+60)
#	elif is_banned(update.message.text, domains):
#		context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
#		context.bot.send_message(chat_id=GROUP_ID, text="<b>"+update.message.from_user.first_name + '</b>, don`t spread adverts here!', parse_mode='html')

#def command_ban(update:Update, context:CallbackContext):
#	user = update.message.from_user
#	if not update.message.reply_to_message:
#		update.message.reply_text('This command should be a reply to message')
#	else:
#		if is_admin(context.bot.get_chat_administrators(update.effective_chat.id), user.id):
#			context.bot.send_message(chat_id=GROUP_ID, text="<b>"+update.message.reply_to_message.from_user.first_name + '</b> was banned for 1 hour. Cause: disobeying to terms of use.', parse_mode='html')
#			context.bot.restrict_chat_member(chat_id=GROUP_ID, user_id=update.message.reply_to_message.from_user.id, permissions=None, until_date=time()+3600)
#		else:
#			context.bot.send_message(chat_id=1273666675, text=f"User [{user.first_name}](tg://user?id={user.id}) reported to [{update.message.reply_to_message.from_user.first_name}]({update.message.reply_to_message.from_user.id}) to this [message](https://t.me/Modering11/{update.message.reply_to_message.message_id})", parse_mode='markdown')


def ask_location(update, context):
	butt = ReplyKeyboardMarkup([KeyboardButton('Send Location', request_location=True)])
	update.message.reply_text('Salom', reply_markup=butt)

def doubled_text(text):
	return text + ' ' + text
	
def main():
	up = Updater('TOKEN HERE!', use_context=True)

	dp = up.dispatcher

	dp.add_handler(CommandHandler('locate', ask_location))

	up.start_polling()
	up.idle()


if __name__ == '__main__':
	main()
