import asyncio
import logging
import random
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError, ChannelInvalidError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

logger = logging.getLogger(__name__)

class UserBot:
    def __init__(self, api_id, api_hash, phone_number, session_name, db, target_group_id, daily_limit, sleep_interval):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.phone_number = phone_number
        self.db = db
        self.target_group_id = target_group_id
        self.daily_limit = daily_limit
        self.sleep_interval = sleep_interval

    async def start(self):
        await self.client.start(phone=self.phone_number)
        logger.info(f"Userbot {self.phone_number} started.")

    async def add_members(self, account_id, source_group_id):
        today = datetime.now().strftime('%Y-%m-%d')
        daily_count = self.db.get_daily_count(account_id)
        
        if daily_count >= self.daily_limit:
            logger.info(f"Account {account_id} has reached daily limit of {self.daily_limit} members.")
            return

        try:
            # Validate source group
            try:
                source_group = await self.client.get_entity(source_group_id)
            except ChannelInvalidError:
                logger.error(f"Account {account_id} cannot access source group {source_group_id}. Ensure the userbot is a member.")
                raise ValueError(f"Cannot access source group {source_group_id}. Join the group first.")
            target_group = await self.client.get_entity(self.target_group_id)
            
            # Fetch members with retry for flood wait
            try:
                members = await self.client.get_participants(source_group, limit=200)  # Reduced limit to avoid flood
            except FloodWaitError as e:
                logger.error(f"Account {account_id} hit flood limit on GetParticipantsRequest. Waiting {e.seconds} seconds.")
                await asyncio.sleep(e.seconds)
                members = await self.client.get_participants(source_group, limit=200)
                
            target_members = await self.client.get_participants(target_group, limit=200)
            target_member_ids = {member.id for member in target_members}

            # Shuffle members to avoid predictable order
            random.shuffle(members)

            for member in members:
                if daily_count >= self.daily_limit:
                    logger.info(f"Account {account_id} reached daily limit of {self.daily_limit} members.")
                    break

                # Skip bots or users already in target group
                if member.bot or member.id in target_member_ids:
                    if member.id in target_member_ids:
                        logger.info(f"Account {account_id} skipped member {member.id} as they are already in target group.")
                    continue

                # Check if member is an admin
                is_admin = False
                try:
                    participants = await self.client.get_participants(source_group, search=str(member.id), limit=1)
                    for participant in participants:
                        if isinstance(participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                            is_admin = True
                            break
                    if is_admin:
                        logger.info(f"Account {account_id} skipped member {member.id} as they are an admin.")
                        continue
                except FloodWaitError as e:
                    logger.error(f"Account {account_id} hit flood limit on admin check. Waiting {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                    continue
                except Exception as e:
                    logger.warning(f"Account {account_id} could not check admin status for member {member.id}: {e}")
                    continue

                try:
                    start_time = datetime.now()
                    await self.client(InviteToChannelRequest(
                        channel=target_group,
                        users=[member]
                    ))
                    daily_count += 1
                    self.db.update_daily_count(account_id, daily_count)
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Account {account_id} added member {member.id} to target group in {elapsed_time:.2f} seconds.")
                    if self.sleep_interval > 0:
                        await asyncio.sleep(self.sleep_interval)  # Delay to avoid flood

                except UserPrivacyRestrictedError:
                    logger.warning(f"Account {account_id} skipped member {member.id} due to privacy settings.")
                    continue
                except FloodWaitError as e:
                    logger.error(f"Account {account_id} hit flood limit on InviteToChannelRequest. Waiting {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                    continue
                except Exception as e:
                    logger.error(f"Account {account_id} error adding member {member.id}: {e}")
                    continue

        except ValueError as e:
            logger.error(f"Account {account_id} error: {e}")
        except Exception as e:
            logger.error(f"Account {account_id} error: {e}")

    async def get_member_count(self, group_id):
        try:
            group = await self.client.get_entity(group_id)
            participants = await self.client.get_participants(group, limit=0)
            return participants.total
        except FloodWaitError as e:
            logger.error(f"Account {account_id} hit flood limit on GetParticipantsRequest. Waiting {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
            return await self.client.get_participants(group, limit=0).total
        except Exception as e:
            logger.error(f"Error fetching member count for group {group_id}: {e}")
            raise

    async def run_until_disconnected(self):
        await self.client.run_until_disconnected()