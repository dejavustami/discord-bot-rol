import os
import discord
from discord.ext import commands
import random
import asyncio

# --- YETKİLER ---
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.voice_states = True 

bot = commands.Bot(command_prefix=['!', '.'], intents=intents)

# --- SHIP MESAJLARI ---
yuksek = ["Sahilde el ele yürüyüşe ne dersiniz? ✨", "Nikah şahidiniz ben olacağım!", "Siz gerçekseniz diğerleri simülasyon."]
orta = ["Şu anlık kankasınız ama her an her şey olabilir.", "Bir kahve her şeyi çözer.", "Bakışmalar var!"]
dusuk = ["Başka hayatlarda belki bir arada...", "Sistem 'olmaz' diyor.", "Zorlamayın, olmuyor."]

@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı!')

# --- SHIP KOMUTU ---
class ShipView(discord.ui.View):
    def __init__(self, yuzde, renk):
        super().__init__()
        self.add_item(discord.ui.Button(label=f"%{yuzde} Uyum", style=renk, disabled=True))

@bot.command(name="ship")
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2: return await ctx.send("❌ Yeterli üye yok!")

    kisi1, kisi2 = random.sample(uyeler, 2)
    yuzde = random.randint(0, 100)
    
    if yuzde >= 70:
        msg, color, btn = random.choice(yuksek), 0xff0000, discord.ButtonStyle.danger
    elif yuzde >= 40:
        msg, color, btn = random.choice(orta), 0xffcc00, discord.ButtonStyle.success
    else:
        msg, color, btn = random.choice(dusuk), 0x808080, discord.ButtonStyle.secondary

    embed = discord.Embed(
        title="💞 Ship Merkezi",
        description=f"**{kisi1.mention}** & **{kisi2.mention}**\n\n> {msg}",
        color=color
    )
    embed.set_thumbnail(url=kisi1.display_avatar.url)
    embed.set_footer(text=f"{ctx.author.name} istedi.", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed, view=ShipView(yuzde, btn))

# --- DİĞER KOMUTLAR ---
@bot.command()
async def katıl(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect(self_deaf=True, self_mute=True)
        await ctx.send("🎤 Sese girildi!")

@bot.command()
async def temizle(ctx, miktar: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=miktar + 1)

# Render için Token'ı al ve çalıştır
TOKEN = os.getenv('TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("HATA: TOKEN bulunamadı!")
