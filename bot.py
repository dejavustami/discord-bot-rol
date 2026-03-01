import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. RENDER PORT HATASI ---
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

bot = commands.Bot(command_prefix=['!', '.'], intents=intents) # Hem ! hem . ile çalışır

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214
ROL_ID = 1473455349729067151
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 

# --- 3. SHIP MESAJLARI VE SOHBET HAFIZASI ---
ship_mesajlari = {
    "yuksek": [
        "Sahilde el ele yürüyüşe ne dersiniz? ✨",
        "Bu aşkın önünde dağlar bile duramaz!",
        "Düğün davetiyemi şimdiden hazırlıyorum...",
        "Çiğköfte & Milkshake yapmaya ne dersiniz? 🌯🥤",
        "Siz gerçekseniz diğerleri sadece simülasyon!",
        "Evren bile sizin birleşmeniz için çabalıyor.",
        "Aşk kokusu buraya kadar geldi!"
    ],
    "orta": [
        "Biraz çaba ile bu iş olur gibi...",
        "Şu anlık kankasınız ama her an her şey olabilir.",
        "Bir kahve içseniz buzlar erir.",
        "Bakışmalar var ama icraat yok!",
        "Sinema randevusu bu işi çözer."
    ],
    "dusuk": [
        "Başka hayatlarda belki bir arada...",
        "Aralarında kutuplar kadar mesafe var.",
        "Sizden olsa olsa iyi bir düşman olur.",
        "Birbirinizin yanından geçseniz selam vermezsiniz.",
        "Sistem bile 'olmaz' diyor, zorlamayın.",
        "İmkansız aşk dedikleri tam olarak bu."
    ]
}

sohbet_hafizasi = {"selam": "Aleyküm selam!", "naber": "İyidir senden?"}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} aktif! Ship sistemi eklendi.')

# --- 4. GELİŞMİŞ SHIP KOMUTU (.ship) ---
@bot.command(name="ship")
async def ship(ctx):
    # Sunucudaki bot olmayan üyeleri listele
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2:
        return await ctx.send("❌ Shiplenmek için yeterli üye yok!")

    # Rastgele iki kişi seç
    kisi1 = random.choice(uyeler)
    kisi2 = random.choice(uyeler)
    while kisi1 == kisi2: # Aynı kişi seçilirse tekrar seç
        kisi2 = random.choice(uyeler)

    yuzde = random.randint(0, 100)
    
    # Yüzdeye göre mesaj kategorisini seç
    if yuzde >= 70:
        mesaj = random.choice(ship_mesajlari["yuksek"])
        renk = discord.Color.red()
    elif yuzde >= 40:
        mesaj = random.choice(ship_mesajlari["orta"])
        renk = discord.Color.gold()
    else:
        mesaj = random.choice(ship_mesajlari["dusuk"])
        renk = discord.Color.dark_gray()

    embed = discord.Embed(
        title="💞 Ship Merkezi",
        description=f"**[ {kisi1.name} & {kisi2.name} ]**\n\n**%{yuzde}** {mesaj}",
        color=renk
    )
    # Fotoğrafları yan yana görselleştirmek için (Kod basitliği adına avatar linklerini kullanır)
    embed.set_thumbnail(url=kisi1.display_avatar.url)
    embed.set_footer(text=f"{ctx.author.name} tarafından istendi.", icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)

# --- 5. SES, PAYLAŞIM VE DİĞER KOMUTLAR ---
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
        for a in ctx.message.attachments:
            await ctx.send(file=await a.to_file())
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
