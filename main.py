# main.py - Using your own bot to check status
import discord
from discord.ext import commands, tasks
import os
import asyncio

BOT_ID_TO_MONITOR = 1481568432267853886
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
CHECK_INTERVAL = 60

class MonitorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        self.last_status = None
        self.webhook_url = WEBHOOK_URL
    
    async def setup_hook(self):
        self.monitor_bot.start()
        print("Monitor started")
    
    @tasks.loop(seconds=CHECK_INTERVAL)
    async def monitor_bot(self):
        """Check if the bot is online"""
        try:
            # Try to get the bot user
            bot_user = await self.fetch_user(BOT_ID_TO_MONITOR)
            
            if bot_user:
                status = True
                print(f"Bot found: {bot_user.name}")
            else:
                status = False
            
            if self.last_status != status:
                await self.send_status_update(status)
                self.last_status = status
                
        except discord.NotFound:
            await self.send_status_update(False)
            self.last_status = False
            print("Bot not found")
        except Exception as e:
            print(f"Error: {e}")
    
    async def send_status_update(self, is_online):
        """Send webhook update"""
        if not self.webhook_url:
            return
        
        if is_online:
            emoji = "🟢"
            message = "Bot is currently working"
            color = 0x00FF00
        else:
            emoji = "🔴"
            message = "Bot is not working! Please DO NOT ping the owners or DM them!"
            color = 0xFF0000
        
        embed = discord.Embed(
            title="🤖 Bot Status",
            description=f"{emoji} Bot is **{'ONLINE' if is_online else 'OFFLINE'}**",
            color=color
        )
        embed.add_field(name="Status", value=f"{emoji} {'ONLINE' if is_online else 'OFFLINE'}", inline=True)
        embed.add_field(name="Bot ID", value=str(BOT_ID_TO_MONITOR), inline=True)
        embed.add_field(name="Message", value=message, inline=False)
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.webhook_url, session=session)
            await webhook.send(embed=embed)
    
    @monitor_bot.before_loop
    async def before_monitor(self):
        await self.wait_until_ready()

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not set!")
        print("You need a bot token to monitor other bots")
        exit(1)
    
    if not WEBHOOK_URL:
        print("ERROR: WEBHOOK_URL not set!")
        exit(1)
    
    bot = MonitorBot()
    bot.run(TOKEN)
