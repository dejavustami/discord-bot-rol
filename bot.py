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

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214
ROL_ID = 1473455349729067151
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

# --- 3. SOHBET HAFIZASI ---
sohbet_hafizasi = {
    "selam": "Aleyküm selam, hoş geldin canım!",
    "naber": "İyidir bebegim, senden naber?",
    "zonnax": "Efendim askoo?",
    "günaydın": "Günaydın, günün harika geçsin! ✨"
}

invites = {} 
last_messages = {}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} aktif! Cümle içi tarama devrede.')
    if not ghost_mention.is_running(): ghost_mention.start()

# --- 4. PANEL KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ekle(ctx, kelime: str, *, cevap: str):
    sohbet_hafizasi[kelime.lower()] = cevap
    await ctx.send(f"✅ Eklendi! Artık cümlenin içinde **{kelime}** geçerse cevap vereceğim.")

@bot.command()
@commands.has_permissions(administrator=True)
async def liste(ctx):
    liste_metni = "\n".join([f"**{k}** -> {v}" for k, v in sohbet_hafizasi.items()])
    embed = discord.Embed(title="🤖 Sohbet Paneli", description=liste_metni or "Liste boş.", color=0x7289da)
    await ctx.send(embed=embed)

# --- 5. PAYLAŞIM, SOHBET VE KORUMA ---
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

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    msg_content = message.content.lower()

    # --- CÜMLE İÇİ KELİME TARAMA ---
    for kelime, cevap in sohbet_hafizasi.items():
        if kelime in msg_content: # Eğer kelime mesajın herhangi bir yerindeyse
            await message.channel.send(f"{message.author.mention} {cevap}")
            break # Birden fazla cevap vermesin diye durduruyoruz

    # --- KORUMA SİSTEMİ ---
    if not message.author.guild_permissions.administrator:
        if re.search(r'(https?://\S+)', message.content) and "!paylas" not in message.content:
            await message.delete()
            return await message.channel.send(f"🚫 Link yasak!", delete_after=3)
        
        if len(message.content) > 10 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7:
            await message.delete()
            return await message.channel.send(f"🚫 Bağırma!", delete_after=3)

    await bot.process_commands(message)

# --- 6. DİĞERLERİ ---
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
    if channel and channel.guild.members:
        online = [m for m in channel.guild.members if m.status != discord.Status.offline and not m.bot]
        if online:
            target = random.choice(online)
            m = await channel.send(f"{target.mention} Gözüm üzerinde!")
            await asyncio.sleep(2)
            await m.delete()

bot.run(TOKEN)
