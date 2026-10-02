from highrise import BaseBot, User, Position
import random, asyncio, json, os, time
from flask import Flask
import threading

# Flask - Render icin 7/24 ayakta tutma
app = Flask(__name__)
@app.route('/')
def home():
    return "Guvenlik DJ Bot AKTIF! rraviee"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

class Bot(BaseBot):
    SAHIP = "rraviee"

    FLOSS = "dance-floss"
    GUARD_OUTFIT = ["shirt-m-securityjacket", "pants-m-securitypants", "shoes-m_securityboots", "hat-m_securitycap"]
    JAIL_POS = Position(0, 0, 0, "FrontRight")

    def __init__(self):
        super().__init__()
        self.kredi = {}
        self.last_daily = {}
        self.jailed = {}
        self.tp_acik = True
        self.load_data()

    def load_data(self):
        if os.path.exists("data.json"):
            try:
                d = json.load(open("data.json"))
                self.kredi = d.get("kredi", {})
                self.last_daily = d.get("daily", {})
            except:
                pass

    def save_data(self):
        json.dump({"kredi": self.kredi, "daily": self.last_daily}, open("data.json","w"))

    async def on_start(self, session):
        print(f"BOT AKTIF: {session.room_info.room_name} | Sahip: {self.SAHIP}")
        try:
            await self.highrise.set_outfit([{"id": item} for item in self.GUARD_OUTFIT])
            print("Güvenlik kıyafeti giyildi")
        except Exception as e:
            print(f"Kıyafet hatası: {e}")

        await self.highrise.chat("🛡️ GÜVENLİK DJ BOT AKTİF! Sahip: rraviee | Modlar kullanabilir! -daily ile 50 kredi al | -komutlar yaz | Floss açık 🎧")
        asyncio.create_task(self.floss_loop())
        asyncio.create_task(self.jail_loop())

    async def floss_loop(self):
        while True:
            try:
                await self.highrise.send_emote(self.FLOSS)
                await asyncio.sleep(7)
            except:
                await asyncio.sleep(5)

    async def jail_loop(self):
        while True:
            now = time.time()
            for uname, unjail_time in list(self.jailed.items()):
                if now >= unjail_time:
                    del self.jailed[uname]
                    await self.highrise.chat(f"🔓 {uname} Silivri'den çıktı!")
            await asyncio.sleep(10)

    async def get_user_by_name(self, name):
        try:
            users = (await self.highrise.get_room_users()).content
            name = name.replace("@","").lower()
            for u, p in users:
                if u.username.lower() == name:
                    return u, p
        except:
            pass
        return None, None

    async def is_mod_check(self, user: User):
        if user.username.lower() == self.SAHIP.lower():
            return True
        try:
            priv = await self.highrise.get_room_privilege(user.id)
            if priv:
                return True
        except:
            return False
        return False

    async def on_chat(self, user: User, message: str):
        if not message.startswith("-"):
            return
        parts = message[1:].split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]
        username = user.username.lower()
        is_owner = username == self.SAHIP.lower()
        is_mod = is_owner or await self.is_mod_check(user)

        if cmd == "daily":
            last = self.last_daily.get(username, 0)
            if time.time() - last < 86400:
                kalan = int(86400 - (time.time() - last))
                saat = kalan // 3600
                await self.highrise.chat(f"@{user.username} Günlük kredini zaten aldın! {saat} saat sonra tekrar gel 💰")
            else:
                self.kredi[username] = self.kredi.get(username, 0) + 50
                self.last_daily[username] = time.time()
                self.save_data()
                await self.highrise.chat(f"@{user.username} 50 kredi verildi! Toplam kredin: {self.kredi[username]} 💰")
            return

        if cmd == "komutlar":
            await self.highrise.chat("MOD: -daily -ban/-mute @kişi süre -kick @kişi -unmute/-unban @kişi -double @kişi emote_id -punch @kişi -clown @kişi -sum @kişi -tele x y z / @kişi -jail @kişi dk | ADMIN: -tp 1/0 -come -punch all -emote emote_id")
            return

        if cmd in ["ban","mute","kick","unmute","unban","double","punch","clown","sum","tele","jail","tp","come","emote"]:
            if not is_mod:
                await self.highrise.chat(f"@{user.username} Bu komutu sadece modlar kullanabilir! 🛡️")
                return

        if cmd in ["ban", "mute"]:
            if len(args) < 2:
                await self.highrise.chat(f"Kullanım: -{cmd} @Kullanıcı süre_saniye Örn: -ban @emre 3600")
                return
            target, _ = await self.get_user_by_name(args[0])
            if not target:
                await self.highrise.chat(f"Kullanıcı bulunamadı: {args[0]}")
                return
            if target.username.lower() == self.SAHIP.lower():
                await self.highrise.chat("Sahibi banlayamazsın!")
                return
            try:
                sure = int(args[1])
                await self.highrise.moderate_room(target.id, cmd, sure)
                await self.highrise.chat(f"🛡️ @{target.username} {sure} saniye {cmd}lendi! (komut: @{user.username})")
            except Exception as e:
                await self.highrise.chat(f"Hata: {e}")

        elif cmd == "kick":
            if not args:
                await self.highrise.chat("Kullanım: -kick @Kullanıcı")
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                if target.username.lower() == self.SAHIP.lower():
                    return
                await self.highrise.moderate_room(target.id, "kick")
                await self.highrise.chat(f"@{target.username} odadan atıldı! 👢 (atan: @{user.username})")

        elif cmd in ["unmute", "unban"]:
            if not args:
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                tip = cmd.replace("un","")
                await self.highrise.moderate_room(target.id, tip, 0)
                await self.highrise.chat(f"@{target.username} {tip} kaldırıldı ✅")

        elif cmd == "double":
            if len(args) < 2:
                await self.highrise.chat("Kullanım: -double @Kullanıcı emote_id Örn: -double @ayse dance-tiktok8")
                return
            target, _ = await self.get_user_by_name(args[0])
            emote_id = args[1]
            if target:
                try:
                    await self.highrise.send_emote(emote_id, target.id)
                    await self.highrise.chat(f"💃 @{user.username} + @{target.username} -> {emote_id}")
                except:
                    await self.highrise.chat(f"Emote bulunamadı: {emote_id}. Tüm emote idleri geçerli!")

        elif cmd == "punch":
            if args and args[0].lower() == "all":
                if not is_owner:
                    await self.highrise.chat(" -punch all sadece rraviee kullanabilir! 🛡️")
                    return
                room_users = (await self.highrise.get_room_users()).content
                await self.highrise.chat("👊 HERKESE SAĞ KROŞE GELİYOR!")
                for u, p in room_users:
                    if u.id!= self.highrise.my_id:
                        try:
                            await self.highrise.send_emote("emote-punch", u.id)
                            await asyncio.sleep(0.3)
                        except:
                            pass
            elif args:
                target, _ = await self.get_user_by_name(args[0])
                if target:
                    await self.highrise.send_emote("emote-punch", target.id)
                    await self.highrise.chat(f"👊 @{user.username} -> @{target.username} SAĞ KROŞE!")

        elif cmd == "clown":
            if not args:
                await self.highrise.chat("Kullanım: -clown @Kullanıcı")
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                await self.highrise.chat(f"🤡 @{target.username} clown spam başladı!")
                for i in range(6):
                    try:
                        await self.highrise.send_emote(random.choice(["emote-clown","dance-weird","emote-laughing","emote-greedy"]), target.id)
                        await asyncio.sleep(1)
                    except:
                        pass

        elif cmd == "sum":
            if not args:
                await self.highrise.chat("Kullanım: -sum @Kullanıcı")
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                room_users = (await self.highrise.get_room_users()).content
                my_pos = None
                for u, p in room_users:
                    if u.id == self.highrise.my_id:
                        my_pos = p
                        break
                if my_pos:
                    await self.highrise.teleport(target.id, Position(my_pos.x+1, my_pos.y, my_pos.z, my_pos.facing))
                    await self.highrise.chat(f"@{target.username} yanına ışınlandı! 📍")

        elif cmd == "tele":
            if not self.tp_acik and not is_owner:
                await self.highrise.chat("Teleport kapalı! Sahip -tp 1 ile açabilir.")
                return
            if len(args) >= 3:
                try:
                    x = float(args[0]); y = float(args[1]); z = float(args[2])
                    await self.highrise.teleport(self.highrise.my_id, Position(x, y, z, "FrontRight"))
                    await self.highrise.chat(f"📍 {x} {y} {z} konumuna ışınlandım!")
                except:
                    await self.highrise.chat("Kordinat hatalı! Örn: -tele 10 0 5")
            elif len(args) == 1:
                target, tpos = await self.get_user_by_name(args[0])
                if target and tpos:
                    await self.highrise.teleport(self.highrise.my_id, Position(tpos.x+1, tpos.y, tpos.z, tpos.facing))
                    await self.highrise.chat(f"@{target.username} yanına ışınlandım!")
                else:
                    await self.highrise.chat(f"Kullanıcı bulunamadı: {args[0]}")
            else:
                await self.highrise.chat("Kullanım: -tele x y z veya -tele @Kullanıcı")

        elif cmd == "jail":
            if len(args) < 2:
                await self.highrise.chat("Kullanım: -jail @Kullanıcı ceza_dakikası Örn: -jail @troll 5")
                return
            target, _ = await self.get_user_by_name(args[0])
            if not target:
                return
            if target.username.lower() == self.SAHIP.lower():
                await self.highrise.chat("Sahibi jailleyemezsin!")
                return
            try:
                dakika = int(args[1])
                self.jailed[target.username.lower()] = time.time() + dakika*60
                await self.highrise.teleport(target.id, self.JAIL_POS)
                await self.highrise.chat(f"🚔 @{target.username} {dakika} dakika Silivri'ye gönderildi! :D (cezalayan: @{user.username})")
            except:
                await self.highrise.chat("Dakika hatalı!")

        elif cmd == "tp":
            if not is_owner:
                await self.highrise.chat("Bu komut sadece rraviee kullanabilir!")
                return
            if args and args[0] in ["1","0"]:
                self.tp_acik = args[0] == "1"
                await self.highrise.chat(f"Teleport {'açıldı ✅' if self.tp_acik else 'kapandı ❌'}")
            else:
                await self.highrise.chat(f"TP durumu: {'açık' if self.tp_acik else 'kapalı'} | Kullanım: -tp 1/0")

        elif cmd == "come":
            room_users = (await self.highrise.get_room_users()).content
            for u, p in room_users:
                if u.username.lower() == user.username.lower():
                    await self.highrise.teleport(self.highrise.my_id, Position(p.x+1, p.y, p.z, p.facing))
                    await self.highrise.chat(f"@{user.username} yanına geldim! 📍")
                    break

        elif cmd == "emote":
            if not args:
                await self.highrise.chat("Kullanım: -emote emote_id Örn: -emote dance-floss - Tüm emote'ları yapar!")
                return
            emote_id = args[0]
            room_users = (await self.highrise.get_room_users()).content
            await self.highrise.chat(f"Herkese {emote_id} gönderiyorum! 💃")
            for u, p in room_users:
                if u.id!= self.highrise.my_id:
                    try:
                        await self.highrise.send_emote(emote_id, u.id)
                        await asyncio.sleep(0.2)
                    except:
                        pass

    async def on_tip(self, sender: User, receiver: User, tip):
        if receiver.id == self.highrise.my_id:
            try:
                gold = int(tip.amount)
                kredi_ver = gold * 3
                uname = sender.username.lower()
                self.kredi[uname] = self.kredi.get(uname, 0) + kredi_ver
                self.save_data()
                await self.highrise.chat(f"@{sender.username} {gold}g attı! {kredi_ver} kredi verildi! Toplam: {self.kredi[uname]} 💰 ~1g=3 Kredi")
            except Exception as e:
                print(f"Tip hatası: {e}")

# Calistirma
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    from highrise.__main__ import BotDefinition
    ROOM_ID = os.getenv("ROOM_ID", "6ab95573b2ca25fa545f08d3")
    TOKEN = os.getenv("BOT_TOKEN", "c7659afef1ef226636c556580a7c296809ce708d64979038ca14e391e4bb54c9")
    asyncio.run(BotDefinition(Bot(), ROOM_ID, TOKEN).run())
