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
intents.voice_states = True # SES YETKİSİ EKLENDİ

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214
ROL_ID = 1473455349729067151
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

sohbet_hafizasi = {
    "selam": "Aleyküm selam, hoş geldin canım!",
    "naber": "İyidir bebegim, senden naber?",
    "zonnax": "Efendim askoo?",
    "günaydın": "Günaydın, günün harika geçsin! ✨"
}

invites = {} 

@bot.event
async def on_ready():
    print(f'Bot {bot.user} aktif! Ses sistemi hazır.')
    if not ghost_mention.is_running(): ghost_mention.start()

# --- 3. SES KANALINA KATILMA KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def katıl(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # Kanala bağlanırken mikrofon ve kulaklığı kapatır (self_deaf ve self_mute)
        vc = await channel.connect(self_deaf=True, self_mute=True)
        await ctx.send(f"🎤 **{channel.name}** kanalına kulaklık ve mikrofon kapalı şekilde katıldım!")
    else:
        await ctx.send("❌ Önce bir ses kanalına girmen lazım!")

@bot.command()
@commands.has_permissions(administrator=True)
async def ayrıl(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Ses kanalından ayrıldım.")
    else:
        await ctx.send("❌ Zaten bir ses kanalında değilim.")

# --- 4. PANEL VE PAYLAŞIM KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ekle(ctx, kelime: str, *, cevap: str):
    sohbet_hafizasi[kelime.lower()] = cevap
    await ctx.send(f"✅ Eklendi! Cümle içinde **{kelime}** geçerse cevap vereceğim.")

@bot.command()
@commands.has_permissions(administrator=True)
async def paylas(ctx, *, mesaj: str):
    if not ctx.message.attachments:
        return await ctx.send("❌ Videoları yükle!", delete_after=3)
    for attachment in ctx.message.attachments:
        file = await attachment.to_file()
        await ctx.send(file=file)
    final_msg = await ctx.send(mesaj)
    await final_msg.add_reaction("✅")
    try: await ctx.message.delete()
    except: pass

# --- 5. MESAJ KONTROLÜ (SOHBET VE KORUMA) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    msg_content = message.content.lower()

    # Sohbet tarama
    for kelime, cevap in sohbet_hafizasi.items():
        if kelime in msg_content:
            await message.channel.send(f"{message.author.mention} {cevap}")
            break

    # Koruma
    if not message.author.guild_permissions.administrator:
        if re.search(r'(https?://\S+)', message.content) and "!paylas" not in message.content:
            await message.delete()
            return await message.channel.send(f"🚫 Link yasak!", delete_after=3)

    await bot.process_commands(message)

# --- 6. DİĞER SİSTEMLER (TEMİZLE, ROL) ---
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

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member: await member.remove_roles(role)

@tasks.loop(hours=3)
async def ghost_mention():
    secilen_kanal_id = random.choice(KANAL_LISTESI)
    channel = bot.get_channel(secilen_kanal_id)
    if channel:
        online = [m for m in channel.guild.members if m.status != discord.Status.offline and not m.bot]
        if online:
            target = random.choice(online)
            m = await channel.send(f"{target.mention} Gözüm üzerinde!")
            await asyncio.sleep(2)
            await m.delete()

bot.run(TOKEN)
