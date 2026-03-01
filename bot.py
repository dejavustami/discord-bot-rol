import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. RENDER PORT HATASI ENGELLEYİCİ ---
class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), S)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 2. AYARLAR ---
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.reactions = True        
intents.invites = True 
intents.voice_states = True 

bot = commands.Bot(command_prefix=['!', '.'], intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214
ROL_ID = 1473455349729067151
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 

# --- 3. SHIP MESAJLARI VE HAFIZA ---
yuksek = ["Sahilde el ele yürüyüşe ne dersiniz? ✨", "Düğün davetiyemi hazırlıyorum...", "Gerçek aşk bu olsa gerek!"]
orta = ["Şu anlık kankasınız ama her an her şey olabilir.", "Bir kahve her şeyi çözer.", "Bakışmalar var!"]
dusuk = ["Başka hayatlarda belki bir arada...", "Sistem 'olmaz' diyor.", "Kutuplar kadar uzaksınız."]

sohbet_hafizasi = {"selam": "Aleyküm selam!", "naber": "İyidir senden?"}

# --- 4. BUTONLU SHIP SİSTEMİ ---
class ShipView(discord.ui.View):
    def __init__(self, kisi1, kisi2, yuzde, mesaj, renk):
        super().__init__()
        # Butona tıklandığında hiçbir şey yapmasın, sadece süs
        self.add_item(discord.ui.Button(label=f"%{yuzde} Uyum", style=renk, disabled=True))

@bot.command(name="ship")
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2: return await ctx.send("❌ Yeterli üye yok!")

    kisi1 = random.choice(uyeler)
    kisi2 = random.choice(uyeler)
    while kisi1 == kisi2: kisi2 = random.choice(uyeler)

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
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2I1dmV4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41JWZ5996f64/giphy.gif") # Hareketli kalp gif'i
    embed.set_footer(text=f"{ctx.author.name} tarafından istendi.", icon_url=ctx.author.display_avatar.url)

    view = ShipView(kisi1, kisi2, yuzde, msg, btn)
    await ctx.send(embed=embed, view=view)

# --- 5. DİĞER KOMUTLAR (KATIL, PAYLAS, EKLE) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def katıl(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect(self_deaf=True, self_mute=True)
        await ctx.send("🎤 Sese girildi!")

@bot.command()
@commands.has_permissions(administrator=True)
async def paylas(ctx, *, mesaj: str):
    if ctx.message.attachments:
        for a in ctx.message.attachments: await ctx.send(file=await a.to_file())
        m = await ctx.send(mesaj)
        await m.add_reaction("✅")
        await ctx.message.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def ekle(ctx, kelime: str, *, cevap: str):
    sohbet_hafizasi[kelime.lower()] = cevap
    await ctx.send(f"✅ '{kelime}' eklendi.")

# --- 6. MESAJ KONTROLÜ ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    msg = message.content.lower()
    for k, v in sohbet_hafizasi.items():
        if k in msg:
            await message.channel.send(f"{message.author.mention} {v}")
            break
    await bot.process_commands(message)

bot.run(TOKEN)
