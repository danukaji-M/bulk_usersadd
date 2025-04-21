import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    try:
        config = {
            'API_ID': [os.getenv('API_ID_1'), os.getenv('API_ID_2')],
            'API_HASH': [os.getenv('API_HASH_1'), os.getenv('API_HASH_2')],
            'PHONE_NUMBERS': [os.getenv('PHONE_NUMBER_1'), os.getenv('PHONE_NUMBER_2')],
            'BOT_TOKEN': os.getenv('BOT_TOKEN'),
            'TARGET_GROUP_ID': int(os.getenv('TARGET_GROUP_ID')),
            'ADMIN_USER_ID': int(os.getenv('ADMIN_USER_ID')),
            'DAILY_LIMIT_PER_ACCOUNT': int(os.getenv('DAILY_LIMIT_PER_ACCOUNT')),
            'SLEEP_INTERVAL': int(os.getenv('SLEEP_INTERVAL')),
        }
        
        # Validate configuration
        for i, (api_id, api_hash, phone) in enumerate(zip(config['API_ID'], config['API_HASH'], config['PHONE_NUMBERS'])):
            if not all([api_id, api_hash, phone]):
                raise ValueError(f"Missing API_ID, API_HASH, or PHONE_NUMBER for account {i+1}")
        if not config['BOT_TOKEN']:
            raise ValueError("BOT_TOKEN is missing")
        if not config['TARGET_GROUP_ID']:
            raise ValueError("TARGET_GROUP_ID is missing")
        if not config['ADMIN_USER_ID']:
            raise ValueError("ADMIN_USER_ID is missing")
        if config['DAILY_LIMIT_PER_ACCOUNT'] <= 0:
            raise ValueError("DAILY_LIMIT_PER_ACCOUNT must be positive")
        if config['SLEEP_INTERVAL'] <= 0:
            raise ValueError("SLEEP_INTERVAL must be positive")

        return config
    except Exception as e:
        raise ValueError(f"Configuration error: {e}")