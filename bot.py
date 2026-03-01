import os
import discord
from discord.ext import commands
import random

# --- SHIP MESAJI HAVUZU (TEKRARLANMASIN DİYE GENİŞLETİLDİ) ---
yuksek_havuz = [
    "Sahilde el ele yürüyüşe ne dersiniz? ✨", "Düğün davetiyemi hazırlıyorum...", 
    "Gerçek aşk bu olsa gerek!", "Siz gerçekseniz diğerleri simülasyon.", 
    "Çiğköfte & milkshake yapalım mı? 🌯🥤", "Evren sizin için birleşti.",
    "Bakışlarınızdan aşk akıyor.", "Sizin aşkınız dilden dile dolaşacak.",
    "Nikah şahidiniz ben olacağım!", "Birbirinizin ruh eşisiniz."
]

orta_havuz = [
    "Şu anlık kankasınız ama her an her şey olabilir.", "Bir kahve her şeyi çözer.", 
    "Bakışmalar var ama icraat yok!", "Sinema randevusu bu işi bitirir.",
    "Kıvılcımlar çakıyor ama ateş yanmamış.", "Gelirse başka hayatlarda belki...",
    "Biraz çaba ile bu iş olur gibi.", "Frekanslar uyuşuyor."
]

dusuk_havuz = [
    "Başka hayatlarda belki bir arada...", "Sistem 'olmaz' diyor.", 
    "Kutuplar kadar uzaksınız.", "Zorlamayın, olmuyor.",
    "Yıldızlarınız hiç barışmamış.", "Sizden olsa olsa iyi bir düşman olur.",
    "Aynı odada bile duramazsınız.", "Mantık 'kaçıın' diyor."
]

class ShipView(discord.ui.View):
    def __init__(self, yuzde, renk):
        super().__init__()
        self.add_item(discord.ui.Button(label=f"%{yuzde} Uyum", style=renk, disabled=True))

@bot.command(name="ship")
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2: return await ctx.send("❌ Yeterli üye yok!")

    kisi1 = random.choice(uyeler)
    kisi2 = random.choice(uyeler)
    while kisi1 == kisi2: kisi2 = random.choice(uyeler)

    yuzde = random.randint(0, 100)
    
    # Yeni ve Güvenli Gif Linkleri
    if yuzde >= 70:
        msg, color, btn = random.choice(yuksek_havuz), 0xff0000, discord.ButtonStyle.danger
        gif = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp1eHRnd3U4OHo1Z2t3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/26BRv0ThflsHCqfJA/giphy.gif"
    elif yuzde >= 40:
        msg, color, btn = random.choice(orta_havuz), 0xffcc00, discord.ButtonStyle.success
        gif = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnhhM256Z2t3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41JWZ5996f64/giphy.gif"
    else:
        msg, color, btn = random.choice(dusuk_havuz), 0x808080, discord.ButtonStyle.secondary
        gif = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp1eHRnd3U4OHo1Z2t3Z3R3Z3R3Z3R3Z3R3Z3R3Z3R3JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif"

    embed = discord.Embed(
        title="💞 Ship Merkezi",
        description=f"**{kisi1.mention}** & **{kisi2.mention}**\n\n> {msg}",
        color=color
    )
    embed.set_thumbnail(url=kisi1.display_avatar.url)
    embed.set_image(url=gif) # Hatasız yeni gif linki
    embed.set_footer(text=f"{ctx.author.name} tarafından istendi.", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed, view=ShipView(yuzde, btn))
