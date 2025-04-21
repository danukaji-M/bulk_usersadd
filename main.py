import asyncio
import logging
from config.config import get_config
from database.db import Database
from bot.telegram_bot import TelegramBot
from userbot.userbot import UserBot

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Load configuration
    config = get_config()

    # Initialize database
    db = Database()

    # Initialize userbots
    userbots = [
        UserBot(
            api_id=config['API_ID'][i],
            api_hash=config['API_HASH'][i],
            phone_number=config['PHONE_NUMBERS'][i],
            session_name=f'session_{i}',
            db=db,
            target_group_id=config['TARGET_GROUP_ID'],
            daily_limit=config['DAILY_LIMIT_PER_ACCOUNT'],
            sleep_interval=config['SLEEP_INTERVAL']
        )
        for i in range(len(config['API_ID']))
    ]

    # Initialize bot
    bot = TelegramBot(
        bot_token=config['BOT_TOKEN'],
        admin_user_id=config['ADMIN_USER_ID'],
        db=db,
        add_members_callback=lambda account_id, source_group_id: userbots[account_id].add_members(account_id, source_group_id),
        get_member_count_callback=lambda account_id, group_id: userbots[account_id].get_member_count(group_id)
    )
    bot.initialize_tasks(len(userbots))

    # Start userbots
    for userbot in userbots:
        await userbot.start()

    # Start bot
    await bot.start()

    # Keep userbots running
    await asyncio.gather(*(userbot.run_until_disconnected() for userbot in userbots))

if __name__ == "__main__":
    asyncio.run(main())