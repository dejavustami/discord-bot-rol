import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- RENDER PORT HİLESİ ---
class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), S)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- AYARLAR VE INTENTS ---
intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
intents.reactions = True        
intents.invites = True # Davetleri takip etmek için gerekli

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214  # Rol alma kanalı
ROL_ID = 1473455349729067151    # Verilecek rol
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1248468672171868214 # Üye giriş mesajının gideceği kanal
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

invites = {} # Davetleri tutacak sözlük

@bot.event
async def on_ready():
    print(f'Bot {bot.user} aktif ve davetleri tarıyor!')
    # Mevcut davetleri her sunucu için kaydet
    for guild in bot.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except:
            pass
    if not ghost_mention.is_running():
        ghost_mention.start()

# --- ÜYE KATILINCA (DM + KANAL MESAJI) ---
@bot.event
async def on_member_join(member):
    # Davet edeni bulma işlemi
    inviter_name = "Bilinmiyor"
    try:
        before = invites.get(member.guild.id, [])
        after = await member.guild.invites()
        invites[member.guild.id] = after
        for invite in before:
            if invite.uses < next((i.uses for i in after if i.code == invite.code), 0):
                inviter_name = invite.inviter.name
                break
    except:
        pass

    # 1. Kanala Mesaj Atma
    channel = bot.get_channel(HOSGELDIN_KANAL_ID)
    if channel:
        toplam = len(member.guild.members)
        await channel.send(f"📥 **{member.name}**, **{inviter_name}** tarafından davet edildi ve sunucuda **{toplam}** kişi olduk!")

    # 2. Üyeye DM Atma
    try:
        embed = discord.Embed(
            title=f"ZONNAX'a hoş geldin!",
            description=f"Selam {member.name}, kanalları görmek için tike basmayı unutma: <#{KANAL_ID}>",
            color=discord.Color.purple()
        )
        await member.send(embed=embed)
    except:
        pass

# --- TİKE BASINCA ROL VERME ---
@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member and not member.bot:
            await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == KANAL_ID and str(payload.emoji) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(ROL_ID)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)

# --- SOHBET VE ETİKETLEME ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    if msg == "selam":
        await message.channel.send("Selam, hoş geldin!")
    elif msg == "naber":
        await message.channel.send("İyi senden naber?")
    await bot.process_commands(message)

@tasks.loop(hours=3)
async def ghost_mention():
    secilen = bot.get_channel(random.choice(KANAL_LISTESI))
    if secilen:
        onlines = [m for m in secilen.guild.members if m.status != discord.Status.offline and not m.bot]
        if onlines:
            target = random.choice(onlines)
            m = await secilen.send(f"{target.mention} Göz atmayı unutma!")
            await asyncio.sleep(2)
            await m.delete()

bot.run(TOKEN)
