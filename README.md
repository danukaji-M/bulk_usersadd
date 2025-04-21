# Telegram Userbot

A Python project to add members from a public Telegram group to another group using two userbot accounts, controlled via a Telegram bot. The bot supports `/start group_id` to initiate adding members, `/report` to show the number of added members, and `/check_members group_id` to check the member count of a group. It adds up to 20 members per day per account, respects privacy settings, skips existing members and admins, and sends reports every 30 minutes.

## Prerequisites

- Python 3.8+
- Telegram accounts (2) with API credentials from https://my.telegram.org
- Telegram bot token from BotFather
- Admin rights for userbots in both source and target groups

## Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd telegram_userbot
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the** `.env` **file**:

   - Copy the example below and replace the placeholders with your values:

     ```plaintext
     API_ID_1=27499311
     API_HASH_1=4d50117ac059959d0e4010d1820cff16
     PHONE_NUMBER_1=+94771456593
     API_ID_2=22862192
     API_HASH_2=98375d0646c10f0d40de4393fe30078c
     PHONE_NUMBER_2=+94714437765
     BOT_TOKEN=7578848649:AAHAVbtPj05i8AXSnbL4qVMAgltrde4sTzs
     TARGET_GROUP_ID=-1002357656013
     ADMIN_USER_ID=7809101082
     DAILY_LIMIT_PER_ACCOUNT=20
     SLEEP_INTERVAL=10
     ```

   - Save it as `.env` in the project root.

5. **Run the project**:

   ```bash
   python main.py
   ```

   - On first run, log in to each userbot account by entering the phone number and the code sent by Telegram.

## Bot Commands

- `/start group_id`: Start adding members from the specified public group (e.g., `/start -1001165778496`).
- `/report`: Get the number of members added by each account today.
- `/check_members group_id`: Check the number of members in the specified group (e.g., `/check_members -1001165778496`).

## Notes

- The script adds up to 20 members per day per account with a 10-second delay between additions to minimize flood risks.
- **Warning**: Rapid member addition increases the risk of `FloodWaitError` or account bans. Monitor logs for flood errors and use secondary accounts.
- Users with privacy settings, admins, or those already in the target group are skipped and not counted in added members.
- Reports are sent every 30 minutes to the admin user ID via the bot.
- A SQLite database (`userbot.db`) tracks added members persistently.
- To further reduce flood errors, increase `SLEEP_INTERVAL` in `.env` (e.g., to 15 seconds) or lower `DAILY_LIMIT_PER_ACCOUNT`.
- Telegram’s anti-spam policies are strict. Use responsibly to avoid account bans.

## Troubleshooting

- **FloodWaitError**: The script retries after the wait time, but frequent errors indicate too many requests. Increase `SLEEP_INTERVAL` to 15 or reduce `DAILY_LIMIT_PER_ACCOUNT` to 10. Check logs for wait times (e.g., "Waiting 26s on GetParticipantsRequest").
- **Login issues**: Ensure API credentials and phone numbers are correct in `.env`.
- **Bot not responding**: Verify `BOT_TOKEN` and `ADMIN_USER_ID` in `.env`. Use `@GetIDsBot` to confirm your user ID.
- **Member count errors**: Ensure the userbot is a member of the group or has access to it.
- **No members added**:
  - Check logs for privacy restrictions, existing members, or flood limits.
  - **"Could not find the input entity for PeerChannel"**: The userbot is not a member of the source group (e.g., `-1001165778496`). Join both userbots (`+94771456593`, `+94714437765`) manually or via an invite link for private groups. Test with `/check_members -1001165778496` to confirm access.
  - **"could not check admin status ... bytes or str expected"**: Update to the latest `userbot/userbot.py`, which uses `search=str(member.id)` for admin checks.
  - **"could not check admin status ... a TLObject was expected"**: Ensure you’re using the latest `userbot/userbot.py` with corrected admin check logic.
- **Group access errors**: Use `/check_members group_id` to verify the userbot can access the group. If not, join the group with the userbot accounts.

## License

This project is for educational purposes. Ensure compliance with Telegram’s Terms of Service.