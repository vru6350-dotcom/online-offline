# main.py - Enhanced with debugging
import aiohttp
import asyncio
import os

BOT_ID = 1481568432267853886
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
CHECK_INTERVAL = 60

async def check_bot_status():
    """Check if bot exists and is accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Checking bot ID: {BOT_ID}")
            async with session.get(f'https://discord.com/api/v10/users/{BOT_ID}') as response:
                print(f"API Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Bot Name: {data.get('username')}")
                    return True
                elif response.status == 404:
                    print("Bot not found - Invalid ID or bot doesn't exist")
                    return False
                else:
                    print(f"Unexpected status: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"Error checking bot: {e}")
        return False

async def send_webhook(is_online):
    """Send webhook with status"""
    if not WEBHOOK_URL:
        print("WEBHOOK_URL not set!")
        return False
    
    if is_online:
        emoji = "🟢"
        message = "Bot is currently working"
        color = 0x00FF00
        status_text = "ONLINE"
    else:
        emoji = "🔴"
        message = "Bot is not working! Please DO NOT ping the owners or DM them!"
        color = 0xFF0000
        status_text = "OFFLINE"
    
    embed = {
        "embeds": [{
            "title": "🤖 Bot Status",
            "description": f"{emoji} Bot is **{status_text}**",
            "color": color,
            "fields": [
                {
                    "name": "Status",
                    "value": f"{emoji} {status_text}",
                    "inline": True
                },
                {
                    "name": "Bot ID",
                    "value": str(BOT_ID),
                    "inline": True
                },
                {
                    "name": "Message",
                    "value": message,
                    "inline": False
                }
            ]
        }]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=embed) as response:
                if response.status in [200, 204]:
                    print(f"✅ Webhook sent: Bot is {status_text}")
                    return True
                else:
                    print(f"❌ Webhook failed: {response.status}")
                    return False
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return False

async def monitor():
    """Main monitoring loop with initial check"""
    print("=" * 50)
    print("Bot Status Monitor Starting...")
    print(f"Bot ID: {BOT_ID}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print(f"Webhook: {'SET' if WEBHOOK_URL else 'NOT SET'}")
    print("=" * 50)
    
    # Do initial check immediately
    print("\nPerforming initial check...")
    initial_status = await check_bot_status()
    print(f"Initial status: {'ONLINE' if initial_status else 'OFFLINE'}")
    
    if initial_status:
        await send_webhook(True)
    else:
        await send_webhook(False)
    
    last_status = initial_status
    
    # Main loop
    while True:
        try:
            await asyncio.sleep(CHECK_INTERVAL)
            
            current_status = await check_bot_status()
            
            if last_status != current_status:
                print(f"Status changed! Was: {last_status}, Now: {current_status}")
                await send_webhook(current_status)
                last_status = current_status
            
        except Exception as e:
            print(f"Monitor error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("ERROR: WEBHOOK_URL environment variable not set!")
        print("\nPlease add it in Railway:")
        print("Variables tab → Add Variable → WEBHOOK_URL = your_webhook_url")
        exit(1)
    
    asyncio.run(monitor())
