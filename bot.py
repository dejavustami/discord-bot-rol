import os
import discord
from discord.ext import commands, tasks
import asyncio
import random
from easy_pil import Editor, load_image_async, Font # Görsel oluşturmak için kütüphane
import aiohttp
from io import BytesIO

# ... (Koda ait diğer importlar ve başlangıç ayarları aynen kalacak)

sohbet_hafizasi = {"selam": "Aleyküm selam!", "naber": "İyidir senden?"}

# Ship mesaj listesi (Daha fazla ekleyebilirsin)
yuksek_mesajlar = [
    "Sahilde yürüyüşe ne dersiniz? ✨",
    "Düğün davetiyemi hazırlıyorum...",
    "Birbiriniz için yaratılmışsınız!",
    "Aşkın önünde dağlar duramaz."
]
orta_mesajlar = [
    "Şu anlık kankasınız ama her an her şey olabilir.",
    "Bir kahve içseniz buzlar erir.",
    "Bakışmalar var ama icraat yok!",
    "Sinema randevusu bu işi çözer."
]
dusuk_mesajlar = [
    "Başka hayatlarda belki bir arada...",
    "Aralarında kutuplar kadar mesafe var.",
    "Sizden iyi bir düşman olur.",
    "Sistem 'olmaz' diyor."
]

@bot.event
async def on_ready():
    print(f'Bot {bot.user} aktif! Görsel panel hazır.')

# --- GELİŞMİŞ GÖRSEL SHIP KOMUTU (.ship) ---
@bot.command(name="ship")
async def ship(ctx):
    # Sunucudaki bot olmayan üyeleri listele
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2:
        return await ctx.send("❌ Shiplenmek için yeterli üye yok!")

    # Rastgele iki kişi seç
    kisi1 = random.choice(uyeler)
    kisi2 = random.choice(uyeler)
    while kisi1 == kisi2: kisi2 = random.choice(uyeler)

    yuzde = random.randint(0, 100)
    
    # Mesaj ve Kalp Rengi Belirleme
    if yuzde >= 70:
        mesaj = random.choice(yuksek_mesajlar)
        kalp_rengi = "#e81224" # Kırmızı (Romantik)
    elif yuzde >= 40:
        mesaj = random.choice(orta_mesajlar)
        kalp_rengi = "#ffc107" # Sarı (Arkadaşlık/Orta)
    else:
        mesaj = random.choice(dusuk_mesajlar)
        kalp_rengi = "#6c757d" # Gri (Soğuk)

    # Arka plan ve Avatarları Hazırlama
    background = Editor(BytesIO(b'\x00'*4), width=1000, height=400, color="#1a1a1a") # Koyu arka plan
    
    try:
        # Avatarları İnternetten Çekme
        pfp1 = await load_image_async(str(kisi1.display_avatar.url_as(format="png")))
        pfp2 = await load_image_async(str(kisi2.display_avatar.url_as(format="png")))
        
        # Avatarları Resme Yerleştirme ve Yuvarlama
        pfp1_img = Editor(pfp1).resize(300, 300).circle_image()
        pfp2_img = Editor(pfp2).resize(300, 300).circle_image()
        
        background.paste(pfp1_img, (100, 50))
        background.paste(pfp2_img, (600, 50))
        
        # Ortaya Kalp Yerleştirme
        heart = Editor("heart.png").resize(150, 150) # 'heart.png' dosyasının botun klasöründe olması gerekir
        background.paste(heart, (425, 125))
        
        # Metinleri Yazma
        font = Font.poppins(size=50)
        user_font = Font.poppins(size=30)
        
        #
        background.text((500, 300), f"", font=user_font, color="white", align="center")
        #
        background.text((500, 360), f"%{yuzde} {mesaj}", font=font, color="white", align="center")
        
        # Resmi Gönderme
        file = discord.File(fp=background.image_bytes, filename="ship.png")
        await ctx.send(file=file)
        
    except Exception as e:
        await ctx.send(f"❌ Görsel oluşturulurken bir hata oluştu. (Sıradan Embed gönderiliyor)\nHata: {e}")
        # Hata durumunda eski basit Embed'i gönderelim
        # ... (Eski basit embed kodu)

# ... (Kodun geri kalanı sese katıl, paylas, ekle vb. aynen kalacak)

bot.run(TOKEN)
