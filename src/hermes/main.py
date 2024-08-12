import asyncio
from logging_config import logger
from config.settings import TELEGRAM_BOT_TOKEN
from config.bot_instance import client
from utils.handler_decorator import handler_collector
import utils.handler_telegram

def register_handlers(client):
    try:
        for event_type, handler in handler_collector.handlers:
            client.add_event_handler(handler, event_type)
        logger.info("Handlers registered successfully.")
    except Exception as e:
        logger.error("Failed to register handlers.", exc_info=True)
        raise

async def main():
    try:
        await client.start(bot_token=TELEGRAM_BOT_TOKEN)
        logger.info("Bot has started.")
        register_handlers(client)
        await client.run_until_disconnected()

    except Exception as e:
        logger.error("An error occurred during bot operation.", exc_info=True)

    finally:
        await client.disconnect()
        logger.info("Bot has been disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
