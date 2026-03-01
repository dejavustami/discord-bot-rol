import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. RENDER PORT HATASI ENGELLEYİCİ ---
# Render'ın "Port Hatası" vermemesi için küçük bir sunucu başlatır
class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), S)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 2. AYARLAR VE YETKİLER ---
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.reactions = True        
intents.invites = True 
intents.voice_states = True 

bot = commands.Bot(command_prefix=['!', '.'], intents=intents)

# Değişkenler
TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214 # Rol verme kanalı
ROL_ID = 1473455349729067151   # Verilecek rol
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 

# Sohbet ve Ship Hafızası
sohbet_hafizasi = {"selam": "Aleyküm selam, hoş geldin canım!", "naber": "İyidir bebegim, senden naber?"}
yuksek_havuz = ["Sahilde el ele yürüyüşe ne dersiniz? ✨", "Nikah şahidiniz ben olacağım!", "Siz gerçekseniz diğerleri simülasyon."]
orta_havuz = ["Şu anlık kankasınız ama her an her şey olabilir.", "Bir kahve her şeyi çözer.", "Bakışmalar var!"]
dusuk_havuz = ["Başka hayatlarda belki bir arada...", "Sistem 'olmaz' diyor.", "Zorlamayın, olmuyor."]

@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak aktif ve tüm sistemler hazır!')

# --- 3. BUTONLU SHIP SİSTEMİ (.ship) ---
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
        msg, color, btn = random.choice(yuksek_havuz), 0xff0000, discord.ButtonStyle.danger
    elif yuzde >= 40:
        msg, color, btn = random.choice(orta_havuz), 0xffcc00, discord.ButtonStyle.success
    else:
        msg, color, btn = random.choice(dusuk_havuz), 0x808080, discord.ButtonStyle.secondary

    embed = discord.Embed(title="💞 Ship Merkezi", description=f"**{kisi1.mention}** & **{kisi2.mention}**\n\n> {msg}", color=color)
    embed.set_thumbnail(url=kisi1.display_avatar.url)
    embed.set_footer(text=f"{ctx.author.name} tarafından istendi.", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed, view=ShipView(yuzde, btn))

# --- 4. VİDEO PAYLAŞIM VE SOHBET PANELİ ---
@bot.command()
@commands.has_permissions(administrator=True)
async def paylas(ctx, *, mesaj: str):
    if not ctx.message.attachments:
        return await ctx.send("❌ Önce videoları yükle!", delete_after=3)
    for attachment in ctx.message.attachments:
        await ctx.send(file=await attachment.to_file())
    final_msg = await ctx.send(mesaj)
    await final_msg.add_reaction("✅")
    try: await ctx.message.delete()
    except: pass

@bot.command()
@commands.has_permissions(administrator=True)
async def ekle(ctx, kelime: str, *, cevap: str):
    sohbet_hafizasi[kelime.lower()] = cevap
    await ctx.send(f"✅ '{kelime}' kelimesi hafızaya eklendi.")

# --- 5. SES KANALINA KATILMA ---
@bot.command()
@commands.has_permissions(administrator=True)
async def katıl(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect(self_deaf=True, self_mute=True)
        await ctx.send("🎤 Ses kanalına kulaklık/mikrofon kapalı girildi!")
    else:
        await ctx.send("❌ Önce bir ses kanalına girmelisin!")

@bot.command()
@commands.has_permissions(administrator=True)
async def ayrıl(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Ses kanalından çıkış yapıldı.")

# --- 6. MESAJ KONTROLÜ (KORUMA + SOHBET) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    msg_content = message.content.lower()

    # Dinamik Sohbet Cevapları
    for kelime, cevap in sohbet_hafizasi.items():
        if kelime in msg_content:
            await message.channel.send(f"{message.author.mention} {cevap}")
            break

    # Koruma Sistemleri (Yönetici değilse)
    if not message.author.guild_permissions.administrator:
        # Link Engelleyici
        if re.search(r'(https?://\S+)', message.content) and "!paylas" not in message.content:
            await message.delete()
            return await message.channel.send("🚫 Link paylaşımı yasaktır!", delete_after=3)

    await bot.process_commands(message)

# --- 7. ROL VERME VE TEMİZLEME ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def temizle(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member and not member.bot: await member.add_roles(role)

# Botu Çalıştır
if TOKEN:
    bot.run(TOKEN)
else:
    print("HATA: Lütfen Render'a TOKEN ekleyin!")
