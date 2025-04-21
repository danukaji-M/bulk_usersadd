import asyncio
import logging
from telegram.ext import Application, CommandHandler
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot_token, admin_user_id, db, add_members_callback, get_member_count_callback):
        self.app = Application.builder().token(bot_token).build()
        self.admin_user_id = admin_user_id
        self.db = db
        self.add_members_callback = add_members_callback
        self.get_member_count_callback = get_member_count_callback
        self.tasks = {}

    async def start_command(self, update, context):
        if update.effective_user.id != self.admin_user_id:
            await update.message.reply_text("Unauthorized.")
            return

        try:
            source_group_id = int(context.args[0])
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /start group_id")
            return

        for account_id in self.tasks:
            if self.tasks[account_id] is None or self.tasks[account_id].done():
                self.tasks[account_id] = asyncio.create_task(
                    self.add_members_callback(account_id, source_group_id)
                )
                await update.message.reply_text(f"Started adding members with Account {account_id+1} from group {source_group_id}.")
            else:
                await update.message.reply_text(f"Account {account_id+1} is already running.")

    async def report_command(self, update, context):
        if update.effective_user.id != self.admin_user_id:
            await update.message.reply_text("Unauthorized.")
            return

        today = datetime.now().strftime('%Y-%m-%d')
        report = f"📊 Daily Report ({today})\n"
        total = 0
        for i in range(len(self.tasks)):
            count = self.db.get_daily_count(i)
            total += count
            report += f"Account {i+1}: {count} members added\n"
        report += f"Total: {total} members added"

        await update.message.reply_text(report)

    async def check_members_command(self, update, context):
        if update.effective_user.id != self.admin_user_id:
            await update.message.reply_text("Unauthorized.")
            return

        try:
            group_id = int(context.args[0])
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /check_members group_id")
            return

        try:
            # Use the first userbot account to check member count
            member_count = await self.get_member_count_callback(0, group_id)
            await update.message.reply_text(f"Group {group_id} has {member_count} members.")
        except Exception as e:
            logger.error(f"Error checking member count for group {group_id}: {e}")
            await update.message.reply_text(f"Error checking member count: {str(e)}")

    async def report_task(self):
        while True:
            today = datetime.now().strftime('%Y-%m-%d')
            report = f"📊 Daily Report ({today})\n"
            total = 0
            for i in range(len(self.tasks)):
                count = self.db.get_daily_count(i)
                total += count
                report += f"Account {i+1}: {count} members added\n"
            report += f"Total: {total} members added"

            try:
                await self.app.bot.send_message(chat_id=self.admin_user_id, text=report)
            except Exception as e:
                logger.error(f"Error sending report: {e}")

            await asyncio.sleep(30 * 60)  # Every 30 minutes

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("report", self.report_command))
        self.app.add_handler(CommandHandler("check_members", self.check_members_command))

    async def start(self):
        self.setup_handlers()
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        asyncio.create_task(self.report_task())

    def initialize_tasks(self, num_accounts):
        self.tasks = {i: None for i in range(num_accounts)}