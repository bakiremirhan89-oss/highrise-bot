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
                now = time.time()
                for uname, unjail_time in list(self.jailed.items()):
                    if now >= unjail_time:
                        del self.jailed[uname]
                        await self.highrise.chat(f"🔓 {uname} Silivri'den cikti! Bir daha uslu dur 😄")
                await asyncio.sleep(10)
            except:
                await asyncio.sleep(10)

    async def kredi_board_loop(self):
        while True:
            await asyncio.sleep(600)
            try:
                if self.kredi:
                    top = sorted(self.kredi.items(), key=lambda x: x[1], reverse=True)[:3]
                    msg = "🏆 KREDI LIDERLERI: "
                    for i, (u, k) in enumerate(top):
                        msg += f"{i+1}. {u}({k}) "
                    await self.highrise.chat(msg)
            except:
                pass

    # ========== YARDIMCI FONKSIYONLAR ==========
    async def get_user_by_name(self, name):
        try:
            users = (await self.highrise.get_room_users()).content
            name = name.replace("@","").lower().strip()
            for u, p in users:
                if u.username.lower() == name:
                    return u, p
        except Exception as e:
            print(f"get_user hatasi: {e}")
        return None, None

    async def is_mod_check(self, user: User):
        if user.username.lower() == self.SAHIP.lower():
            return True
        try:
            priv = await self.highrise.get_room_privilege(user.id)
            if priv is not None:
                return True
        except:
            pass
        return False

    async def on_user_join(self, user: User):
        try:
            msg = random.choice(self.WELCOME_MSGS).format(user=user.username)
            await self.highrise.chat(msg)
        except:
            pass

    # ========== CHAT KOMUTLARI ==========
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

        # --- HERKESIN KOMUTLARI ---
        if cmd == "daily":
            last = self.last_daily.get(username, 0)
            if time.time() - last < 86400:
                kalan = int(86400 - (time.time() - last))
                saat = kalan // 3600
                dk = (kalan % 3600) // 60
                await self.highrise.chat(f"@{user.username} Gunluk kredini zaten aldin! {saat} saat {dk} dk sonra tekrar gel 💰")
            else:
                self.kredi[username] = self.kredi.get(username, 0) + 50
                self.last_daily[username] = time.time()
                self.save_data()
                await self.highrise.chat(f"@{user.username} 50 kredi verildi! Toplam kredin: {self.kredi[username]} 💰")
            return

        if cmd == "kredim" or cmd == "bakiye":
            bakiye = self.kredi.get(username, 0)
            await self.highrise.chat(f"@{user.username} Bakiyen: {bakiye} kredi 💰")
            return

        if cmd == "komutlar" or cmd == "help" or cmd == "komut":
            await self.highrise.chat("📜 HERKES: -daily -kredim")
            await asyncio.sleep(0.5)
            await self.highrise.chat("🛡️ MOD: -ban/-mute @kisi sure -kick @kisi -unmute/-unban @kisi -double @kisi emote_id -punch @kisi -clown @kisi -sum @kisi -tele x y z / @kisi -jail @kisi dk")
            await asyncio.sleep(0.5)
            await self.highrise.chat("👑 SAHIP: -tp 1/0 -come -punch all -emote emote_id")
            return

        # MOD KONTROLU
        if cmd in ["ban","mute","kick","unmute","unban","double","punch","clown","sum","tele","jail","tp","come","emote","afk"]:
            if not is_mod:
                await self.highrise.chat(f"@{user.username} Bu komutu sadece modlar kullanabilir! 🛡️")
                return

        if cmd == "ban" or cmd == "mute":
            if len(args) < 2:
                await self.highrise.chat(f"Kullanim: -{cmd} @Kullanici sure_saniye Orn: -ban @emre 3600")
                return
            target, _ = await self.get_user_by_name(args[0])
            if not target:
                await self.highrise.chat(f"Kullanici bulunamadi: {args[0]}")
                return
            if target.username.lower() == self.SAHIP.lower():
                await self.highrise.chat("Sahibi banlayamazsin! 🛡️")
                return
            try:
                sure = int(args[1])
                await self.highrise.moderate_room(target.id, cmd, sure)
                await self.highrise.chat(f"🛡️ @{target.username} {sure} saniye {cmd}lendi! (komut: @{user.username})")
            except Exception as e:
                await self.highrise.chat(f"Hata: {e}")

        elif cmd == "kick":
            if not args:
                await self.highrise.chat("Kullanim: -kick @Kullanici")
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                if target.username.lower() == self.SAHIP.lower():
                    await self.highrise.chat("Sahibi kickleyemezsin!")
                    return
                await self.highrise.moderate_room(target.id, "kick")
                await self.highrise.chat(f"@{target.username} odadan atildi! 👢 (atan: @{user.username})")

        elif cmd == "unmute" or cmd == "unban":
            if not args:
                await self.highrise.chat(f"Kullanim: -{cmd} @Kullanici")
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                tip = cmd.replace("un","")
                await self.highrise.moderate_room(target.id, tip, 0)
                await self.highrise.chat(f"@{target.username} {tip} kaldirildi ✅ (ac an: @{user.username})")

        elif cmd == "double":
            if len(args) < 2:
                await self.highrise.chat("Kullanim: -double @Kullanici emote_id Orn: -double @ayse dance-tiktok8")
                return
            target, _ = await self.get_user_by_name(args[0])
            emote_id = args[1]
            if target:
                try:
                    await self.highrise.send_emote(emote_id, target.id)
                    await self.highrise.chat(f"💃 @{user.username} + @{target.username} -> {emote_id}")
                except:
                    await self.highrise.chat(f"Emote bulunamadi: {emote_id}. Gecerli emote ID kullan!")

        elif cmd == "punch":
            if args and args[0].lower() == "all":
                if not is_owner:
                    await self.highrise.chat(" -punch all sadece rraviee kullanabilir! 🛡️")
                    return
                room_users = (await self.highrise.get_room_users()).content
                await self.highrise.chat("👊 HERKESE SAG KROSE GELIYOR! @rraviee den")
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
                    await self.highrise.chat(f"👊 @{user.username} -> @{target.username} SAG KROSE!")

        elif cmd == "clown":
            if not args:
                await self.highrise.chat("Kullanim: -clown @Kullanici")
                return
            target, _ = await self.get_user_by_name(args[0])
            if target:
                await self.highrise.chat(f"🤡 @{target.username} clown spam basladi! @rraviee istedi")
                for i in range(6):
                    try:
                        await self.highrise.send_emote(random.choice(["emote-clown","dance-weird","emote-laughing","emote-greedy"]), target.id)
                        await asyncio.sleep(1)
                    except:
                        pass

        elif cmd == "sum":
            if not args:
                await self.highrise.chat("Kullanim: -sum @Kullanici")
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
                    await self.highrise.chat(f"@{target.username} yanina isinlandi! 📍 (cek en: @{user.username})")

        elif cmd == "tele":
            if not self.tp_acik and not is_owner:
                await self.highrise.chat("Teleport kapali! Sahip -tp 1 ile acabilir.")
                return
            if len(args) >= 3:
                try:
                    x = float(args[0]); y = float(args[1]); z = float(args[2])
                    await self.highrise.teleport(self.highrise.my_id, Position(x, y, z, "FrontRight"))
                    await self.highrise.chat(f"📍 {x} {y} {z} konumuna isinlandim!")
                except:
                    await self.highrise.chat("Kordinat hatali! Orn: -tele 10 0 5")
            elif len(args) == 1:
                target, tpos = await self.get_user_by_name(args[0])
                if target and tpos:
                    await self.highrise.teleport(self.highrise.my_id, Position(tpos.x+1, tpos.y, tpos.z, tpos.facing))
                    await self.highrise.chat(f"@{target.username} yanina isinlandim! 📍")
                else:
                    await self.highrise.chat(f"Kullanici bulunamadi: {args[0]}")
            else:
                await self.highrise.chat("Kullanim: -tele x y z veya -tele @Kullanici")

        elif cmd == "jail":
            if len(args) < 2:
                await self.highrise.chat("Kullanim: -jail @Kullanici ceza_dakikasi Orn: -jail @troll 5")
                return
            target, _ = await self.get_user_by_name(args[0])
            if not target:
                await self.highrise.chat(f"Kullanici bulunamadi: {args[0]}")
                return
            if target.username.lower() == self.SAHIP.lower():
                await self.highrise.chat("Sahibi jailleyemezsin! 🛡️")
                return
            try:
                dakika = int(args[1])
                self.jailed[target.username.lower()] = time.time() + dakika*60
                await self.highrise.teleport(target.id, self.JAIL_POS)
                await self.highrise.chat(f"🚔 @{target.username} {dakika} dakika Silivri'ye gonderildi! :D (cezalayan: @{user.username})")
            except:
                await self.highrise.chat("Dakika hatali! Sayi yaz")

        elif cmd == "tp":
            if not is_owner:
                await self.highrise.chat("Bu komut sadece rraviee kullanabilir!")
                return
            if args and args[0] in ["1","0"]:
                self.tp_acik = args[0] == "1"
                await self.highrise.chat(f"Teleport {'acildi ✅' if self.tp_acik else 'kapandi ❌'} | Ayarlayan: rraviee")
            else:
                await self.highrise.chat(f"TP durumu: {'acik ✅' if self.tp_acik else 'kapali ❌'} | Kullanim: -tp 1/0")

        elif cmd == "come":
            if not is_owner:
                await self.highrise.chat("Bu komut sadece rraviee kullanabilir!")
                return
            room_users = (await self.highrise.get_room_users()).content
            for u, p in room_users:
                if u.username.lower() == user.username.lower():
                    await self.highrise.teleport(self.highrise.my_id, Position(p.x+1, p.y, p.z, p.facing))
                    await self.highrise.chat(f"@{user.username} yanina geldim! 📍")
                    break

        elif cmd == "emote":
            if not args:
                await self.highrise.chat("Kullanim: -emote emote_id Orn: -emote dance-floss - Tum emote'lari yapar!")
                return
            emote_id = args[0]
            room_users = (await self.highrise.get_room_users()).content
            await self.highrise.chat(f"Herkese {emote_id} gonderiyorum! 💃 (baslatan: {user.username})")
            for u, p in room_users:
                if u.id!= self.highrise.my_id:
                    try:
                        await self.highrise.send_emote(emote_id, u.id)
                        await asyncio.sleep(0.2)
                    except:
                        pass

    # ========== GOLD / TIP SISTEMI ==========
    async def on_tip(self, sender: User, receiver: User, tip):
        if receiver.id == self.highrise.my_id:
            try:
                gold = int(tip.amount)
                kredi_ver = gold * 3
                uname = sender.username.lower()
                self.kredi[uname] = self.kredi.get(uname, 0) + kredi_ver
                self.save_data()
                await self.highrise.chat(f"@{sender.username} {gold}g atti! {kredi_ver} kredi verildi! Toplam: {self.kredi[uname]} 💰 ~1g=3 Kredi ~ Tesekkurler ❤️")
            except Exception as e:
                print(f"Tip hatasi: {e}")

# ========== CALISTIRMA ==========
if __name__ == "__main__":
    from highrise.__main__ import BotDefinition
    ROOM_ID = os.getenv("ROOM_ID", "6ab95573b2ca25fa545f08d3")
    TOKEN = os.getenv("BOT_TOKEN", "BURAYA_TOKENINI_YAZ")
    asyncio.run(BotDefinition(Bot(), ROOM_ID, TOKEN).run())
