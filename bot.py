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

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214
ROL_ID = 1473455349729067151
EMOJI = '🔞'
HOSGELDIN_KANAL_ID = 1473456025981161535 
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

invites = {} 
last_messages = {}

# --- 3. BOT HAZIR OLDUĞUNDA ---
@bot.event
async def on_ready():
    print(f'Bot {bot.user} aktif! Toplu paylaşım komutu hazır.')
    for guild in bot.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except: pass
    if not ghost_mention.is_running():
        ghost_mention.start()

# --- 4. GÜNCELLENMİŞ: ANLIK TOPLU PAYLAŞIM KOMUTU ---
@bot.command()
@commands.has_permissions(administrator=True)
async def paylas(ctx, mesaj: str, *linkler):
    """
    Kullanım: !paylas "Final Mesajı" link1 link2 link3 ...
    """
    if len(linkler) < 1:
        return await ctx.send("❌ Paylaşılacak link bulamadım!")

    # Tüm videoları aynı anda (hızlıca) atar
    for link in linkler:
        await ctx.send(link)
    
    # En sona mesajı atar ve tik ekler
    final_msg = await ctx.send(mesaj)
    await final_msg.add_reaction("✅")

# --- 5. ÜYE KATILINCA (ETİKETLİ) ---
@bot.event
async def on_member_join(member):
    inviter_name = "Bilinmiyor"
    try:
        before = invites.get(member.guild.id, [])
        after = await member.guild.invites()
        invites[member.guild.id] = after
        for invite in before:
            if invite.uses < next((i.uses for i in after if i.code == invite.code), 0):
                inviter_name = invite.inviter.name
                break
    except: pass

    channel = bot.get_channel(HOSGELDIN_KANAL_ID)
    if channel:
        toplam = len(member.guild.members)
        await channel.send(f"📥 **{member.mention}**, **{inviter_name}** tarafından davet edildi ve sunucuda **{toplam}** kişi olduk!")

# --- 6. OTOMATİK KORUMA (SPAM / CAPS / LINK) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    if not message.author.guild_permissions.administrator:
        # Link Engelleyici
        if re.search(r'(https?://\S+)', message.content):
            if "!paylas" not in message.content:
                await message.delete()
                return await message.channel.send(f"🚫 {message.author.mention}, link yasak!", delete_after=3)

        # Capslock Engelleyici
        if len(message.content) > 5 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7:
            await message.delete()
            return await message.channel.send(f"🚫 {message.author.mention}, bağırma!", delete_after=3)

        # Spam Engelleyici
        author_id = message.author.id
        if author_id in last_messages and last_messages[author_id] == message.content:
            await message.delete()
            return await message.channel.send(f"🚫 {message.author.mention}, spam yapma!", delete_after=3)
        last_messages[author_id] = message.content

    await bot.process_commands(message)

# --- 7. MODERASYON KOMUTLARI ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def temizle(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f'🗑️ {miktar} mesaj temizlendi.', delete_after=3)

# --- 8. TİKE BASINCA ROL VERME ---
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

# --- 9. RASTGELE ETİKETLEME ---
@tasks.loop(hours=3)
async def ghost_mention():
    secilen_kanal_id = random.choice(KANAL_LISTESI)
    channel = bot.get_channel(secilen_kanal_id)
    if channel:
        online_members = [m for m in channel.guild.members if m.status != discord.Status.offline and not m.bot]
        if online_members:
            target = random.choice(online_members)
            m = await channel.send(f"{target.mention} Buraya bak!")
            await asyncio.sleep(2)
            await m.delete()

bot.run(TOKEN)
