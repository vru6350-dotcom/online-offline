# main.py - Simple bot monitor without discord.py
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
            # Try to get bot info - will return 401 if bot exists but needs auth
            async with session.get(f'https://discord.com/api/v10/users/{BOT_ID}') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Bot found: {data.get('username')}")
                    return True
                elif response.status == 401:
                    # 401 means bot exists but needs authentication
                    print(f"✅ Bot exists (needs auth) - assuming online")
                    return True
                elif response.status == 404:
                    print(f"❌ Bot not found")
                    return False
                else:
                    print(f"⚠️ Unexpected status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error checking: {e}")
        return False

async def send_webhook(is_online):
    """Send webhook with status"""
    if not WEBHOOK_URL:
        print("⚠️ WEBHOOK_URL not set!")
        return
    
    if is_online:
        emoji = "🟢"
        message = "Bot is currently working"
        color = 0x00FF00
        status = "ONLINE"
    else:
        emoji = "🔴"
        message = "Bot is not working! Please DO NOT ping the owners or DM them!"
        color = 0xFF0000
        status = "OFFLINE"
    
    payload = {
        "embeds": [{
            "title": "🤖 Bot Status",
            "description": f"{emoji} Bot is **{status}**",
            "color": color,
            "fields": [
                {
                    "name": "Status",
                    "value": f"{emoji} {status}",
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
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status in [200, 204]:
                    print(f"✅ Webhook sent: Bot is {status}")
                else:
                    print(f"❌ Webhook failed: {response.status}")
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")

async def monitor():
    """Main monitoring loop"""
    print("=" * 50)
    print("🤖 Bot Status Monitor Starting...")
    print(f"Bot ID: {BOT_ID}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print(f"Webhook: {'✅ SET' if WEBHOOK_URL else '❌ NOT SET'}")
    print("=" * 50)
    
    # Initial check
    print("\n📡 Performing initial check...")
    initial_status = await check_bot_status()
    print(f"📊 Initial status: {'ONLINE ✅' if initial_status else 'OFFLINE ❌'}")
    
    # Send initial webhook
    await send_webhook(initial_status)
    last_status = initial_status
    
    # Main loop
    while True:
        try:
            await asyncio.sleep(CHECK_INTERVAL)
            
            current_status = await check_bot_status()
            
            if last_status != current_status:
                print(f"🔄 Status changed! Now: {'ONLINE ✅' if current_status else 'OFFLINE ❌'}")
                await send_webhook(current_status)
                last_status = current_status
            
        except Exception as e:
            print(f"❌ Monitor error: {e}")
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
        exit(1)
    
    print("\n🚀 Starting bot monitor...\n")
    asyncio.run(monitor())
