import os
import discord
from discord.ext import commands, tasks
import asyncio
import random

# --- 1. YETKİLER VE AYARLAR ---
intents = discord.Intents.default()
intents.members = True          # Üyeleri görmesi ve DM atması için
intents.message_content = True  # Mesajları okuması (Chat/Ban) için
intents.reactions = True        # Tık atmayı algılaması için

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214  # Tike basılacak kanal ID'si
ROL_ID = 1473455349729067151    # Verilecek rol ID'si
EMOJI = '🔞'                     # Kullanılacak emoji
GHOST_KANAL_ID = 123456789...   # Buraya 3 saatte bir etiket atılacak kanalın ID'sini yaz!

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

# --- 4. YENİ ÜYEYE DM ATMA ---
@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Selam {member.name}, sunucumuza hoş geldin! Sohbetimize bekliyoruz.")
    except:
        print(f"{member.name} kullanıcısının DM'si kapalı.")

# --- 5. SOHBET VE MODERASYON (Ban/Kick) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    msg = message.content.lower()
    if msg == "selam":
        await message.channel.send("Selam, hoş geldin!")
    elif msg == "nasılsın":
        await message.channel.send("İyiyim, sen nasılsın?")
    
    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sebep yok"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} yasaklandı!")

# --- 6. GHOST MENTION (3 Saatte Bir Etiketle ve Sil) ---

@tasks.loop(hours=3)
async def ghost_mention():
    # Buraya istediğin kadar kanal ID'si ekleyebilirsin
    kanal_listesi = [1473455979105489068, 1473455994309705749, 1473455988962234524, 1473456031697993789] 
    
    # Listeden rastgele bir kanal seç
    secilen_kanal_id = random.choice(kanal_listesi)
    channel = bot.get_channel(secilen_kanal_id)
    
    if channel:
        # Seçilen kanaldaki aktif üyeleri bul
        online_members = [m for m in channel.guild.members if m.status != discord.Status.offline and not m.bot]
        
        if online_members:
            target = random.choice(online_members)
            msg = await channel.send(f"{target.mention} Bu kanala da bir göz atmayı unutma!")
            await asyncio.sleep(2)
            await msg.delete()

bot.run(TOKEN)
