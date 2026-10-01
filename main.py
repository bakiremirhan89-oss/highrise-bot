from highrise import BaseBot, User, Position
import random, asyncio, json, os, time
from datetime import datetime

class Bot(BaseBot):
    # ========== AYARLAR ==========
    SAHIP = "rraviee"
    FLOSS = "dance-floss"
    GUARD_OUTFIT = ["shirt-m-securityjacket", "pants-m-securitypants", "shoes-m_securityboots", "hat-m_securitycap"]
    JAIL_POS = Position(0, 0, 0, "FrontRight")
    WELCOME_MSGS = ["Hosgeldin {user}! -daily yazmayi unutma 💰", "Selam {user}! Iyi eglenceler 🎉", "Hey {user} geldi! Floss zamani 💃"]

    def __init__(self):
        super().__init__()
        self.kredi = {}
        self.last_daily = {}
        self.jailed = {}
        self.tp_acik = True
        self.afk_users = {}
        self.spam_kontrol = {}
        self.load_data()

    def load_data(self):
        if os.path.exists("data.json"):
            try:
                d = json.load(open("data.json", "r"))
                self.kredi = d.get("kredi", {})
                self.last_daily = d.get("daily", {})
            except Exception as e:
                print(f"Data yukleme hatasi: {e}")

    def save_data(self):
        try:
            with open("data.json","w") as f:
                json.dump({"kredi": self.kredi, "daily": self.last_daily}, f, indent=2)
        except Exception as e:
            print(f"Data kaydetme hatasi: {e}")

    # ========== BOT BASLADIGINDA ==========
    async def on_start(self, session):
        print(f"[{datetime.now()}] BOT AKTIF: {session.room_info.room_name} | Sahip: {self.SAHIP}")
        try:
            await self.highrise.set_outfit([{"id": item} for item in self.GUARD_OUTFIT])
            print("Guvenlik kiyafeti giyildi")
        except Exception as e:
            print(f"Kiyafet hatasi: {e}")

        await self.highrise.chat("🛡️ GUVENLIK DJ BOT AKTIF! Sahip: rraviee | Modlar kullanabilir! -daily ile 50 kredi al | -komutlar yaz | Floss acik 🎧")
        await asyncio.sleep(1)
        await self.highrise.chat("👑 Komutlar: -ban -mute -kick -jail -punch -clown -double -sum -tele -emote -tp -come")
        asyncio.create_task(self.floss_loop())
        asyncio.create_task(self.jail_loop())
        asyncio.create_task(self.kredi_board_loop())

    async def floss_loop(self):
        while True:
            try:
                await self.highrise.send_emote(self.FLOSS)
                await asyncio.sleep(7)
            except Exception as e:
                print(f"Floss hata: {e}")
                await asyncio.sleep(5)

    async def jail_loop(self):
        while True:
            try:
               
