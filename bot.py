import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render Port Hilesi
class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), S)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# Ayarlar
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.reactions = True        

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214
ROL_ID = 1473455349729067151
EMOJI = '🔞'
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı!')
    if not ghost_mention.is_running():
        ghost_mention.start()

# --- YENİ ÜYE KATILINCA DM ATMA ---
@bot.event
async def on_member_join(member):
    try:
        embed = discord.Embed(
            title=f"ZONNAX'a hoş geldin, {member.name}!",
            description="Sunucuda bu kanaldaki 18+ tikine basarsan kanallar açılır: <#1248468672171868214>\n\nİyi eğlenceler!",
            color=discord.Color.purple()
        )
        await member.send(embed=embed)
    except discord.Forbidden:
        pass

# --- TİKE BASINCA ROL VERME ---
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member and not member.bot:
            await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)

# --- SOHBET KOMUTLARI ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    
    if msg == "selam":
        await message.channel.send("Selam, hoş geldin!")
    elif msg == "naber":
        await message.channel.send("İyi senden naber? 18+ kanallara göz attın mı?")
    elif msg == "zonnax":
        await message.channel.send("Efendim askoo")
    
    await bot.process_commands(message)

# --- RASTGELE ETİKETLEME ---
@tasks.loop(hours=3)
async def ghost_mention():
    secilen_kanal_id = random.choice(KANAL_LISTESI)
    channel = bot.get_channel(secilen_kanal_id)
    if channel:
        online_members = [m for m in channel.guild.members if m.status != discord.Status.offline and not m.bot]
        if online_members:
            target = random.choice(online_members)
            msg = await channel.send(f"{target.mention} Bu kanala da bir göz atmayı unutma!")
            await asyncio.sleep(2)
            await msg.delete()

bot.run(TOKEN)
