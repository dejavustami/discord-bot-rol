import os
import discord
from discord.ext import commands
import asyncio
import random
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# --- 1. RENDER 7/24 AKTİFLİK ---
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

# --- 3. 7/24 SES SİSTEMİ ---
@bot.command()
@commands.has_permissions(administrator=True)
async def katıl(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Önce bir ses kanalına gir!")
    
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    try:
        # Kendi kendine çıkmayı engelleyen ayarlar
        await channel.connect(reconnect=True, self_deaf=True)
        await ctx.send(f"🎤 **{channel.name}** kanalında 7/24 nöbetteyim!")
    except Exception as e:
        await ctx.send(f"⚠️ Bağlantı hatası: {e}")

# --- 4. SHIP SİSTEMİ ---
@bot.command(name="ship")
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2: return
    k1, k2 = ctx.author, random.choice([m for m in uyeler if m.id != ctx.author.id])
    yuzde = random.randint(0, 100)
    embed = discord.Embed(title="💞 Ship Merkezi", description=f"{k1.mention} & {k2.mention}\n\n> Siz gerçekseniz diğerleri simülasyon.", color=0xff0000)
    embed.set_thumbnail(url=k1.display_avatar.url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label=f"%{yuzde} Uyum", style=discord.ButtonStyle.danger, disabled=True))
    await ctx.send(embed=embed, view=view)

# --- 5. KORUMA VE ROL SİSTEMİ ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if not message.author.guild_permissions.administrator:
        if re.search(r'(https?://\S+)', message.content):
            await message.delete()
            return
    await bot.process_commands(message)

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

# --- 6. HOŞ GELDİN ---
@bot.event
async def on_member_join(member):
    kanal = bot.get_channel(HOSGELDIN_KANAL_ID)
    if kanal:
        await kanal.send(f"📥 {member.mention} sunucuya katıldı! **{member.guild.member_count}** kişi olduk! 🎉")

bot.run(TOKEN)
