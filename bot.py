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

# --- 2. AYARLAR VE YETKİLER ---
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

# Hafızalar
sohbet_hafizasi = {"selam": "Aleyküm selam, hoş geldin canım!", "naber": "İyidir bebegim, senden naber?"}
last_messages = {} # Spam kontrolü için

# --- 3. SHIP SİSTEMİ (ID DEĞİL İSİM GÖSTERİR) ---
yuksek = ["Sahilde el ele yürüyüşe ne dersiniz? ✨", "Nikah şahidiniz ben olacağım!", "Siz gerçekseniz diğerleri simülasyon."]
orta = ["Şu anlık kankasınız ama her an her şey olabilir.", "Bir kahve her şeyi çözer.", "Bakışmalar var!"]
dusuk = ["Başka hayatlarda belki bir arada...", "Sistem 'olmaz' diyor.", "Zorlamayın, olmuyor."]

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
    
    if yuzde >= 70: msg, color, btn = random.choice(yuksek), 0xff0000, discord.ButtonStyle.danger
    elif yuzde >= 40: msg, color, btn = random.choice(orta), 0xffcc00, discord.ButtonStyle.success
    else: msg, color, btn = random.choice(dusuk), 0x808080, discord.ButtonStyle.secondary

    # .name kullanarak ID yerine isim yazdırıyoruz
    embed = discord.Embed(title="💞 Ship Merkezi", description=f"**{kisi1.display_name}** & **{kisi2.display_name}**\n\n> {msg}", color=color)
    embed.set_thumbnail(url=kisi1.display_avatar.url)
    await ctx.send(embed=embed, view=ShipView(yuzde, btn))

# --- 4. KORUMA SİSTEMİ (LİNK, CAPS, SPAM) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    # Yönetici değilse kontrolleri yap
    if not message.author.guild_permissions.administrator:
        # 1. Link Engelleyici
        if re.search(r'(https?://\S+)', message.content) and "!paylas" not in message.content:
            await message.delete()
            return await message.channel.send(f"🚫 {message.author.mention}, link yasak!", delete_after=3)

        # 2. Capslock Engelleyici (%70'ten fazlası büyük harfse)
        if len(message.content) > 5:
            upper_count = sum(1 for c in message.content if c.isupper())
            if (upper_count / len(message.content)) > 0.7:
                await message.delete()
                return await message.channel.send(f"🚫 {message.author.mention}, bağırma!", delete_after=3)

        # 3. Spam Engelleyici (Aynı mesajı tekrar ediyorsa)
        author_id = message.author.id
        if author_id in last_messages and last_messages[author_id] == message.content:
            await message.delete()
            return await message.channel.send(f"🚫 {message.author.mention}, spam yapma!", delete_after=3)
        last_messages[author_id] = message.content

    # Sohbet Cevapları
    msg_lower = message.content.lower()
    for k, v in sohbet_hafizasi.items():
        if k in msg_lower:
            await message.channel.send(f"{message.author.mention} {v}")
            break

    await bot.process_commands(message)

# --- 5. HOŞ GELDİN MESAJI ---
@bot.event
async def on_member_join(member):
    kanal = bot.get_channel(HOSGELDIN_KANAL_ID)
    if kanal:
        # Sunucu kişi sayısını gösteren mesaj
        await kanal.send(f"📥 {member.mention}, sunucuya katıldı! Seninle birlikte **{member.guild.member_count}** kişi olduk! 🎉")

# --- 6. VİDEO PAYLAŞIM (!paylas) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def paylas(ctx, *, mesaj: str):
    if not ctx.message.attachments:
        return await ctx.send("❌ Paylaşılacak video bulamadım!", delete_after=3)
    
    for attachment in ctx.message.attachments:
        await ctx.send(file=await attachment.to_file())
    
    final_msg = await ctx.send(mesaj)
    await final_msg.add_reaction("✅")
    try: await ctx.message.delete()
    except: pass

# --- 7. DİĞER KOMUTLAR ---
@bot.command()
@commands.has_permissions(administrator=True)
async def katıl(ctx):
    if ctx.author.voice: await ctx.author.voice.channel.connect(self_deaf=True, self_mute=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def ekle(ctx, kelime: str, *, cevap: str):
    sohbet_hafizasi[kelime.lower()] = cevap
    await ctx.send(f"✅ '{kelime}' eklendi.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def temizle(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)

bot.run(TOKEN)
