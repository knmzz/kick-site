import asyncio
import json
import random
import threading
import time
from datetime import datetime

import tls_client
import websockets

# Buraya Flask paneline aktarılacak loglar gelecek
LOG_LIST = []

def add_log(message):
    LOG_LIST.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    if len(LOG_LIST) > 200:
        LOG_LIST.pop(0)

CLIENT_TOKEN = "e1393935a959b4020a4491574f6490129f678acdaa92760471263db43487f823"


class KickBot:
    def __init__(self, channel, viewer_count):
        self.channel_name = self.clean_channel(channel)
        self.viewer_count = viewer_count

        self.channel_id = None
        self.stream_id = None

        self.stop_flag = False
        self.threads = []
        self.active_connections = 0

    def clean_channel(self, name):
        if "kick.com/" in name:
            return name.split("kick.com/")[1].split("/")[0].split("?")[0]
        return name.lower()

    def get_channel_info(self):
        add_log("Kanal bilgisi alınıyor...")

        try:
            session = tls_client.Session(client_identifier="chrome_120")

            url = f"https://kick.com/api/v2/channels/{self.channel_name}"
            r = session.get(url)

            if r.status_code == 200:
                data = r.json()
                self.channel_id = data.get("id")
                if data.get("livestream"):
                    self.stream_id = data["livestream"].get("id")

                add_log(f"Kanal ID: {self.channel_id}")
                add_log(f"Stream ID: {self.stream_id}")
                return True

            add_log("Kanal bulunamadı.")
            return False

        except Exception as e:
            add_log(f"Kanal bilgisi alınamadı: {e}")
            return False

    def get_token(self):
        try:
            session = tls_client.Session(client_identifier="chrome_120")
            session.headers["X-CLIENT-TOKEN"] = CLIENT_TOKEN

            r = session.get("https://websockets.kick.com/viewer/v1/token")

            if r.status_code == 200:
                token = r.json().get("data", {}).get("token")
                return token

            return None

        except:
            return None

    async def connect_ws(self, token):
        try:
            url = f"wss://websockets.kick.com/viewer/v1/connect?token={token}"

            async with websockets.connect(url) as ws:
                self.active_connections += 1
                add_log(f"Bağlantı açıldı. Aktif: {self.active_connections}")

                handshake = {
                    "type": "channel_handshake",
                    "data": {"message": {"channelId": self.channel_id}}
                }
                await ws.send(json.dumps(handshake))

                for _ in range(10):
                    if self.stop_flag:
                        break

                    await ws.send(json.dumps({"type": "ping"}))
                    await asyncio.sleep(12 + random.randint(1, 5))

        except Exception as e:
            add_log(f"Bağlantı hatası: {e}")

        finally:
            self.active_connections -= 1
            add_log(f"Bağlantı kapandı. Aktif: {self.active_connections}")

    def start_single_connection(self):
        token = self.get_token()
        if not token:
            add_log("Token alınamadı!")
            return

        asyncio.run(self.connect_ws(token))

    def start(self):
        if not self.get_channel_info():
            add_log("Bot başlatılamadı.")
            return

        add_log("Bot çalışmaya başladı!")
        add_log(f"Hedef izleyici: {self.viewer_count}")

        self.stop_flag = False

        for _ in range(self.viewer_count):
            if self.stop_flag:
                break

            t = threading.Thread(target=self.start_single_connection, daemon=True)
            self.threads.append(t)
            t.start()
            time.sleep(0.35)

        add_log("Tüm bağlantılar gönderildi.")

    def stop(self):
        self.stop_flag = True
        add_log("Bot durduruluyor...")
