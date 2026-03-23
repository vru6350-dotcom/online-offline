# simple_monitor.py - Webhook-only monitor
import aiohttp
import asyncio
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_ID = 1481568432267853886
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
CHECK_INTERVAL = 60

STATUS_ONLINE = {
    "emoji": "🟢",
    "message": "Bot is currently working"
}

STATUS_OFFLINE = {
    "emoji": "🔴", 
    "message": "Bot is not working! Please DO NOT ping the owners or DM them!"
}

async def check_bot_status():
    """Check if bot exists/is accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            # Try to get bot info (public endpoint)
            async with session.get(f'https://discord.com/api/v10/users/{BOT_ID}') as response:
                if response.status == 200:
                    return True
                else:
                    return False
    except Exception as e:
        logger.error(f"Error checking: {e}")
        return False

async def send_webhook(status):
    """Send webhook with status"""
    if not WEBHOOK_URL:
        return
    
    try:
        is_online = status
        embed = {
            "embeds": [{
                "title": "Bot Status Monitor",
                "description": f"**Status Update**",
                "color": 0x00FF00 if is_online else 0xFF0000,
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "Status",
                        "value": f"{STATUS_ONLINE['emoji'] if is_online else STATUS_OFFLINE['emoji']} {'ONLINE' if is_online else 'OFFLINE'}",
                        "inline": False
                    },
                    {
                        "name": "Bot ID",
                        "value": str(BOT_ID),
                        "inline": False
                    },
                    {
                        "name": "Message",
                        "value": STATUS_ONLINE['message'] if is_online else STATUS_OFFLINE['message'],
                        "inline": False
                    }
                ],
                "footer": {
                    "text": f"Last checked • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=embed) as response:
                if response.status == 204:
                    logger.info(f"Webhook sent: Bot is {'ONLINE' if is_online else 'OFFLINE'}")
                else:
                    logger.error(f"Failed to send webhook: {response.status}")
                    
    except Exception as e:
        logger.error(f"Error sending webhook: {e}")

async def monitor():
    """Main monitoring loop"""
    last_status = None
    
    while True:
        try:
            current_status = await check_bot_status()
            
            if last_status != current_status:
                await send_webhook(current_status)
                last_status = current_status
                logger.info(f"Status changed to: {'ONLINE' if current_status else 'OFFLINE'}")
            
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL environment variable not set!")
        print("Add it in Railway: WEBHOOK_URL = your_discord_webhook_url")
        exit(1)
    
    print(f"Starting bot monitor for ID: {BOT_ID}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop")
    
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\nMonitor stopped")