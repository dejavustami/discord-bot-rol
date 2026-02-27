import os
import discord
from discord.ext import commands, tasks
import asyncio
import random

# --- 1. YETKİLER VE AYARLAR ---
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.reactions = True        

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214  # Tike basılacak kanal ID'si
ROL_ID = 1473455349729067151    # Verilecek rol ID'si
EMOJI = '🔞'                     # Kullanılacak emoji

# Ghost etiket atılacak kanalların listesi
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

# --- 2. BOT HAZIR OLDUĞUNDA ---
@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı ve şu an aktif!')
    if not ghost_mention.is_running():
        ghost_mention.start()

# --- 3. TİKE BASINCA ROL VERME / ALMA ---
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member and not member.bot:
            await member.add_roles(role)
            print(f'{member.display_name} kullanıcısına rol verildi.')

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)
            print(f'{member.display_name} kullanıcısından rol alındı.')

# --- 4. SOHBET KOMUTLARI ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    msg = message.content.lower()
    if msg == "selam":
        await message.channel.send("Selam, hoş geldin!")
    
    await bot.process_commands(message)

# --- 5. RASTGELE AKTİF ÜYE ETİKETLEME ---
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
