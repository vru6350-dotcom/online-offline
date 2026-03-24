# main.py - Bot Status Monitor
import aiohttp
import asyncio
import os
from datetime import datetime

BOT_ID = 1481568432267853886
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
CHECK_INTERVAL = 60

async def check_bot_status():
    """Check if bot exists in Discord"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://discord.com/api/v10/users/{BOT_ID}') as response:
                return response.status == 200
    except Exception as e:
        print(f"Error checking: {e}")
        return False

async def send_webhook(is_online):
    """Send webhook with status update"""
    if not WEBHOOK_URL:
        print("⚠️ WEBHOOK_URL not set!")
        return
    
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
            "title": "🤖 Bot Status Monitor",
            "description": f"{emoji} **Bot Status Update**",
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Status",
                    "value": f"{emoji} **{status_text}**",
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
            ],
            "footer": {
                "text": f"Monitor checks every {CHECK_INTERVAL} seconds"
            }
        }]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=embed) as response:
                if response.status in [200, 204]:
                    print(f"✅ Webhook sent: Bot is {status_text}")
                else:
                    print(f"❌ Failed to send webhook: {response.status}")
    except Exception as e:
        print(f"Error sending webhook: {e}")

async def monitor():
    """Main monitoring loop"""
    last_status = None
    print("=" * 50)
    print("🤖 Discord Bot Status Monitor")
    print("=" * 50)
    print(f"Monitoring Bot ID: {BOT_ID}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print(f"Webhook: {'✅ Configured' if WEBHOOK_URL else '❌ NOT SET'}")
    print("=" * 50)
    print("Monitor is running... Press Ctrl+C to stop")
    print()
    
    while True:
        try:
            current_status = await check_bot_status()
            
            if last_status is None or last_status != current_status:
                await send_webhook(current_status)
                last_status = current_status
                status_text = "ONLINE ✅" if current_status else "OFFLINE ❌"
                print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Status: {status_text}")
            
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Monitor error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ ERROR: WEBHOOK_URL environment variable not set!")
        print("\nPlease add it in Railway:")
        print("1. Go to your project in Railway")
        print("2. Click 'Variables' tab")
        print("3. Add variable:")
        print("   Key: WEBHOOK_URL")
        print("   Value: your_discord_webhook_url")
        print("\nGet your webhook URL from:")
        print("Discord Server Settings → Integrations → Webhooks → Create Webhook")
        exit(1)
    
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped")