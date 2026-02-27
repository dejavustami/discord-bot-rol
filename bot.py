import os
import discord
from discord.ext import commands

# Bot yetkilerini ayarlıyoruz
intents = discord.Intents.default()
intents.members = True     # Üyeleri görebilmesi için
intents.message_content = True  # Mesajları okuyabilmesi için
intents.reactions = True   # Tepkileri (tık atmayı) algılaması için

bot = commands.Bot(command_prefix='!', intents=intents)

# --- AYARLAR: BURAYI KENDİ BİLGİLERİNLE DOLDUR ---
TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214  # Tike basılacak kanalın ID'si
ROL_ID = 1473455349729067151    # Verilecek rolün ID'si
EMOJI = '🔞'                   # Kullanılacak emoji
# ----------------------------------------------

@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı ve şu an aktif!')

@bot.event
async def on_raw_reaction_add(payload):
    # Sadece belirlediğimiz kanalda ve doğru emojide çalışsın
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)

        if role and member and not member.bot:
            await member.add_roles(role)
            print(f'{member.display_name} kullanıcısına rol verildi.')

@bot.event
async def on_raw_reaction_remove(payload):
    # Tık geri çekilirse rolü geri alsın (İstemiyorsan bu kısmı silebilirsin)
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)

        if role and member:
            await member.remove_roles(role)
            print(f'{member.display_name} kullanıcısından rol alındı.')

bot.run(TOKEN)