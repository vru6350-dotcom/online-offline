# bot_monitor.py - Single file solution
import aiohttp
import asyncio
import os
from datetime import datetime

BOT_ID = 1481568432267853886
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
CHECK_INTERVAL = 60

async def check_bot_status():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://discord.com/api/v10/users/{BOT_ID}') as response:
                return response.status == 200
    except:
        return False

async def send_webhook(is_online):
    if not WEBHOOK_URL:
        return
    
    emoji, msg = ("🟢", "Bot is currently working") if is_online else ("🔴", "Bot is not working! Please DO NOT ping the owners or DM them!")
    
    embed = {
        "embeds": [{
            "title": "🤖 Bot Status",
            "description": f"{emoji} Bot is **{'ONLINE' if is_online else 'OFFLINE'}**",
            "color": 0x00FF00 if is_online else 0xFF0000,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {"name": "Status", "value": f"{emoji} {'ONLINE' if is_online else 'OFFLINE'}", "inline": True},
                {"name": "Bot ID", "value": str(BOT_ID), "inline": True},
                {"name": "Message", "value": msg, "inline": False}
            ]
        }]
    }
    
    async with aiohttp.ClientSession() as session:
        await session.post(WEBHOOK_URL, json=embed)

async def main():
    last = None
    print(f"Monitoring bot {BOT_ID} every {CHECK_INTERVAL}s")
    
    while True:
        try:
            status = await check_bot_status()
            if last != status:
                await send_webhook(status)
                last = status
                print(f"[{datetime.utcnow()}] Bot is {'ONLINE' if status else 'OFFLINE'}")
            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("ERROR: Set WEBHOOK_URL environment variable!")
    else:
        asyncio.run(main())
