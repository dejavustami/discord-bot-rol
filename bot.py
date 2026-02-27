import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
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
intents.invites = True # Davetleri takip etmek için şart

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.getenv('TOKEN')
KANAL_ID = 1248468672171868214  # Tike basılacak kanal ID'si
ROL_ID = 1473455349729067151    # Verilecek rol ID'si
EMOJI = '🔞'

# Üye giriş mesajının gideceği TEK kanal ID'si
HOSGELDIN_KANAL_ID = 1473456025981161535 

# Ghost etiket kanalları
KANAL_LISTESI = [1473455979105489068, 1473455994309705749, 1473455988962234524]

invites = {} 

# --- 3. BOT HAZIR OLDUĞUNDA ---
@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı ve davetleri tarıyor!')
    for guild in bot.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except:
            pass
    if not ghost_mention.is_running():
        ghost_mention.start()

# --- 4. ÜYE KATILINCA (DM + TEK KANAL MESAJI) ---
@bot.event
async def on_member_join(member):
    # Davet edeni tespit etme
    inviter_name = "Bilinmiyor"
    try:
        before = invites.get(member.guild.id, [])
        after = await member.guild.invites()
