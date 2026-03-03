import os
import discord
from discord.ext import commands
import asyncio
import random
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# --- 1. RENDER PORT VE 7/24 AKTİFLİK ---
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
intents.voice_states = True 

bot = commands.Bot(command_prefix=['!', '.'], intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214 
ROL_ID = 1473455349729067151   
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 

sohbet_hafizasi = {"selam": "Aleyküm selam!", "naber": "İyidir bebegim, senden naber?"}
user_message_times = {} 
last_messages = {}

# --- 3. SHIP SİSTEMİ (ETİKETLİ) ---
@bot.command(name="ship")
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2: return await ctx.send("❌ Yeterli üye yok!")
    kisi1 = ctx.author
    kisi2 = random.choice([m for m in uyeler if m.id != kisi1.id])
    yuzde = random.randint(0, 100)
    mesajlar = ["Siz gerçekseniz diğerleri simülasyon.", "Sahilde el ele yürüyüşe ne dersiniz? ✨", "Bu aşkın önünde dağlar duramaz!", "Çiğköfte & milkshake yapalım mı?"]
    embed = discord.Embed(
        title="💞 Ship Merkezi",
        description=f"{kisi1.mention} & {kisi2.mention}\n\n> {random.choice(mesajlar)}",
        color=0xff0000 if yuzde > 70 else 0x808080
    )
    embed.set_thumbnail(url=kisi1.display_avatar.url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label=f"%{yuzde} Uyum", style=discord.ButtonStyle.danger, disabled=True))
    await ctx.send(embed=embed, view=view)

# --- 4. 7/24 SES SİSTEMİ (KESİN ÇÖZÜM) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def katıl(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Bir ses kanalına girmen lazım!")
    
    channel = ctx.author.voice.channel
    
    try:
        # Eğer bot zaten başka bir kanaldaysa oradan ayrıl
        if ctx.voice_client:
            await ctx.voice_client.disconnect(force=True)
            await asyncio.sleep(1)

        # Otomatik yeniden bağlanma (reconnect=True) aktif
        vc = await channel.connect(reconnect=True, self_deaf=True, self_mute=True)
        await ctx.send(f"🎤 **{channel.name}** kanalında 7/24 nöbetteyim!")
        
    except Exception as e:
        await ctx.send(f"❌ Bağlanırken hata oluştu: {e}")

# Ses kanalından biri atarsa veya düşerse geri girme kontrolü
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and after.channel is None:
        if before.channel is not None:
            # 5 saniye bekle ve tekrar girmeyi dene
            await asyncio.sleep(5)
            await before.channel.connect(reconnect=True, self_deaf=True, self_mute=True)

# --- 5. GELİŞMİŞ KORUMA ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    if not message.author.guild_permissions.administrator:
        if re.search(r'(https?://\S+)', message.content) and "!paylas" not in message.content:
            await message.delete()
            return await message.channel.send(f"🚫 {message.author.mention}, link yasak!", delete_after=3)
        
        if len(message.content) > 5:
            if sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7:
                await message.delete()
                return await message.channel.send(f"🚫 {message.author.mention}, bağırma!", delete_after=3)

        uid = message.author.id
        now = time.time()
        if uid not in user_message_times: user_message_times[uid] = []
        user_message_times[uid].append(now)
        user_message_times[uid] = [t for t in user_message_times[uid] if now - t < 5]
        
        if len(user_message_times[uid]) > 4:
            def check(m): return m.author.id == uid
            await message.channel.purge(limit=15, check=check)
            user_message_times[uid] = [] 
            return await message.channel.send(f"⚠️ {message.author.mention}, spam temizlendi!", delete_after=5)

        if uid in last_messages and last_messages[uid] == message.content:
            await message.delete()
            return
        last_messages[uid] = message.content

    msg = message.content.lower()
    for k, v in sohbet_hafizasi.items():
        if k in msg:
            await message.channel.send(f"{message.author.mention} {v}")
            break
    await bot.process_commands(message)

# --- 6. ROL VERME / ALMA (BAS-ÇEK) ---
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member: await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member: await member.remove_roles(role)

# --- 7. HOŞ GELDİN ---
@bot.event
async def on_member_join(member):
    kanal = bot.get_channel(HOSGELDIN_KANAL_ID)
    if kanal:
        await kanal.send(f"📥 {member.mention} geldi! **{member.guild.member_count}** kişiyiz! 🎉")

bot.run(TOKEN)
